"""
Buscador de sanciones OFAC mediante web scraping.
"""

import logging
import time
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import Configuracion
from src.config.constantes import SELECTORES_OFAC, MAX_REINTENTOS, TIEMPO_ENTRE_REINTENTOS

logger = logging.getLogger(__name__)


@dataclass
class ResultadoBusqueda:
    """Resultado de una búsqueda en OFAC."""
    exito: bool
    cantidad_resultados: int = 0
    mensaje_error: Optional[str] = None


class BuscadorOfac:
    """Clase para realizar búsquedas en el sitio OFAC."""

    def __init__(self, navegador: webdriver.Chrome):
        """
        Inicializa el buscador OFAC.

        Args:
            navegador: Instancia del navegador Selenium
        """
        self.navegador = navegador
        self.config = Configuracion()
        self.url_ofac = self.config.selenium.url_ofac
        self.tiempo_espera = self.config.selenium.tiempo_espera_explicito

    def navegar_a_ofac(self) -> bool:
        """
        Navega a la página principal de OFAC y establece zoom al 60%.

        Returns:
            True si la navegación fue exitosa
        """
        try:
            self.navegador.get(self.url_ofac)
            WebDriverWait(self.navegador, self.tiempo_espera).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

            # Establecer zoom al 60% para capturas completas
            try:
                self.navegador.execute_script("document.body.style.zoom='60%'")
                logger.info("Zoom establecido al 60%")
            except Exception as e:
                logger.warning(f"No se pudo establecer el zoom: {e}")

            logger.info("Navegación a OFAC exitosa")
            return True

        except TimeoutException:
            logger.error("Timeout al cargar la página OFAC")
            return False
        except Exception as e:
            logger.error(f"Error al navegar a OFAC: {e}")
            return False

    def buscar_persona(
        self,
        nombre: str,
        direccion: Optional[str] = None,
        pais: Optional[str] = None
    ) -> ResultadoBusqueda:
        """
        Realiza una búsqueda de persona en OFAC.

        Args:
            nombre: Nombre de la persona a buscar
            direccion: Dirección de la persona (opcional)
            pais: País de la persona (opcional)

        Returns:
            Objeto ResultadoBusqueda con el resultado
        """
        for intento in range(MAX_REINTENTOS):
            try:
                self._limpiar_formulario()

                self._llenar_campo_nombre(nombre)

                if direccion:
                    self._llenar_campo_direccion(direccion)

                if pais:
                    self._seleccionar_pais(pais)

                self._hacer_clic_buscar()

                cantidad = self._extraer_cantidad_resultados()

                logger.info(
                    f"Búsqueda completada para '{nombre}': {cantidad} resultados"
                )

                return ResultadoBusqueda(
                    exito=True,
                    cantidad_resultados=cantidad
                )

            except Exception as e:
                logger.warning(
                    f"Intento {intento + 1}/{MAX_REINTENTOS} fallido para '{nombre}': {e}"
                )
                if intento < MAX_REINTENTOS - 1:
                    time.sleep(TIEMPO_ENTRE_REINTENTOS)
                    self.navegar_a_ofac()

        return ResultadoBusqueda(
            exito=False,
            mensaje_error=f"Falló después de {MAX_REINTENTOS} intentos"
        )

    def _llenar_campo_nombre(self, nombre: str) -> None:
        """Llena el campo de nombre en el formulario."""
        campo = WebDriverWait(self.navegador, self.tiempo_espera).until(
            EC.presence_of_element_located(
                (By.ID, "ctl00_MainContent_txtLastName")
            )
        )
        campo.clear()
        campo.send_keys(nombre)

    def _llenar_campo_direccion(self, direccion: str) -> None:
        """Llena el campo de dirección en el formulario."""
        try:
            campo = self.navegador.find_element(
                By.ID, "ctl00_MainContent_txtAddress"
            )
            campo.clear()
            campo.send_keys(direccion)
        except NoSuchElementException:
            logger.warning("Campo de dirección no encontrado")

    def _seleccionar_pais(self, pais: str) -> None:
        """Selecciona el país en el dropdown."""
        try:
            elemento_select = self.navegador.find_element(
                By.ID, "ctl00_MainContent_ddlCountry"
            )
            select = Select(elemento_select)

            # Intentar seleccionar por texto exacto primero
            try:
                select.select_by_visible_text(pais)
                return
            except:
                pass

            # Si no funciona, buscar coincidencia parcial
            for opcion in select.options:
                if pais.lower() in opcion.text.lower():
                    select.select_by_visible_text(opcion.text)
                    return

            logger.warning(f"País '{pais}' no encontrado en el dropdown")

        except NoSuchElementException:
            logger.warning("Campo de país no encontrado")

    def _hacer_clic_buscar(self) -> None:
        """Hace clic en el botón de búsqueda."""
        boton = WebDriverWait(self.navegador, self.tiempo_espera).until(
            EC.element_to_be_clickable(
                (By.ID, "ctl00_MainContent_btnSearch")
            )
        )
        boton.click()

        # Esperar a que aparezca el texto de resultados
        time.sleep(2)  # Pequeña espera para asegurar que los resultados se carguen

    def _limpiar_formulario(self) -> None:
        """Hace clic en el botón Reset para limpiar el formulario."""
        try:
            boton_reset = self.navegador.find_element(
                By.ID, "ctl00_MainContent_btnReset"
            )
            boton_reset.click()
            time.sleep(1)  # Esperar a que se limpie el formulario
        except NoSuchElementException:
            logger.warning("Botón Reset no encontrado")

    def _extraer_cantidad_resultados(self) -> int:
        """
        Extrae la cantidad de resultados de la búsqueda.

        Returns:
            Número de resultados encontrados
        """
        try:
            # Buscar el elemento que contiene "Found"
            elemento_resultado = self.navegador.find_element(
                By.XPATH, "//*[contains(text(), 'Found')]"
            )
            texto = elemento_resultado.text

            # Extraer el numero usando regex: "X Found"
            numeros = re.findall(r'(\d+)\s+Found', texto)
            if numeros:
                return int(numeros[0])

            return 0

        except NoSuchElementException:
            logger.warning("Elemento de conteo de resultados no encontrado")
            return 0
        except Exception as e:
            logger.warning(f"Error al extraer cantidad de resultados: {e}")
            return 0

    def capturar_pantalla(self, ruta_archivo: str) -> bool:
        """
        Captura una screenshot de la página actual.

        Args:
            ruta_archivo: Ruta donde guardar la captura

        Returns:
            True si la captura fue exitosa
        """
        try:
            self.navegador.save_screenshot(ruta_archivo)
            logger.info(f"Captura guardada en: {ruta_archivo}")
            return True
        except Exception as e:
            logger.error(f"Error al capturar pantalla: {e}")
            return False
