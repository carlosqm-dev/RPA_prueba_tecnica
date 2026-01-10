"""
Utilidad para gestión de capturas de pantalla.
"""

import logging
import os
from datetime import datetime
from typing import Optional

from selenium import webdriver

from src.config import Configuracion
from src.config.constantes import FORMATO_FECHA_CAPTURA, FORMATO_NOMBRE_CAPTURA

logger = logging.getLogger(__name__)


class CapturaPantalla:
    """Clase para gestionar capturas de pantalla."""

    def __init__(self, navegador: webdriver.Chrome):
        """
        Inicializa el gestor de capturas.

        Args:
            navegador: Instancia del navegador Selenium
        """
        self.navegador = navegador
        self.config = Configuracion()
        self.directorio = self.config.directorio_capturas

        self._asegurar_directorio()

    def _asegurar_directorio(self) -> None:
        """Crea el directorio de capturas si no existe."""
        if not os.path.exists(self.directorio):
            os.makedirs(self.directorio)
            logger.info(f"Directorio de capturas creado: {self.directorio}")

    def capturar(
        self,
        id_persona: int,
        sufijo: Optional[str] = None
    ) -> Optional[str]:
        """
        Captura la pantalla actual y la guarda con el formato requerido.

        Args:
            id_persona: ID de la persona para nombrar el archivo
            sufijo: Sufijo adicional para el nombre (opcional)

        Returns:
            Ruta del archivo guardado o None si falla
        """
        try:
            fecha = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
            nombre_base = FORMATO_NOMBRE_CAPTURA.format(
                fecha=fecha,
                id_persona=id_persona
            )

            if sufijo:
                nombre_base = nombre_base.replace('.png', f'_{sufijo}.png')

            ruta_completa = os.path.join(self.directorio, nombre_base)

            self.navegador.save_screenshot(ruta_completa)
            logger.info(f"Captura guardada: {ruta_completa}")

            return ruta_completa

        except Exception as e:
            logger.error(f"Error al capturar pantalla: {e}")
            return None

    def capturar_elemento(
        self,
        elemento,
        id_persona: int,
        sufijo: Optional[str] = None
    ) -> Optional[str]:
        """
        Captura un elemento específico de la página.

        Args:
            elemento: Elemento web a capturar
            id_persona: ID de la persona para nombrar el archivo
            sufijo: Sufijo adicional para el nombre (opcional)

        Returns:
            Ruta del archivo guardado o None si falla
        """
        try:
            fecha = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
            nombre_base = f"{fecha}_{id_persona}_elemento"

            if sufijo:
                nombre_base = f"{nombre_base}_{sufijo}"

            nombre_archivo = f"{nombre_base}.png"
            ruta_completa = os.path.join(self.directorio, nombre_archivo)

            elemento.screenshot(ruta_completa)
            logger.info(f"Captura de elemento guardada: {ruta_completa}")

            return ruta_completa

        except Exception as e:
            logger.error(f"Error al capturar elemento: {e}")
            return None

    def listar_capturas(self) -> list:
        """
        Lista todas las capturas en el directorio.

        Returns:
            Lista de rutas de archivos de captura
        """
        try:
            archivos = [
                os.path.join(self.directorio, f)
                for f in os.listdir(self.directorio)
                if f.endswith('.png')
            ]
            return sorted(archivos)
        except Exception as e:
            logger.error(f"Error al listar capturas: {e}")
            return []

    def limpiar_capturas_antiguas(self, dias: int = 30) -> int:
        """
        Elimina capturas más antiguas que el número de días especificado.

        Args:
            dias: Número de días de antigüedad

        Returns:
            Número de archivos eliminados
        """
        import time

        eliminados = 0
        limite = time.time() - (dias * 24 * 60 * 60)

        try:
            for archivo in self.listar_capturas():
                if os.path.getmtime(archivo) < limite:
                    os.remove(archivo)
                    eliminados += 1
                    logger.debug(f"Captura eliminada: {archivo}")

            if eliminados > 0:
                logger.info(f"Se eliminaron {eliminados} capturas antiguas")

            return eliminados

        except Exception as e:
            logger.error(f"Error al limpiar capturas: {e}")
            return eliminados
