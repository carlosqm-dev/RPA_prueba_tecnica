"""
Configuración y gestión del navegador Selenium.
"""

import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.config import Configuracion

logger = logging.getLogger(__name__)

_navegador: Optional[webdriver.Chrome] = None


def crear_navegador(headless: Optional[bool] = None) -> webdriver.Chrome:
    """
    Crea y configura una instancia del navegador Chrome.

    Args:
        headless: Si es True, ejecuta el navegador sin interfaz gráfica.
                  Si es None, usa el valor de configuración.

    Returns:
        Instancia del navegador Chrome configurada
    """
    global _navegador

    if _navegador is not None:
        logger.warning("Ya existe una instancia del navegador")
        return _navegador

    config = Configuracion()

    opciones = Options()

    if headless is None:
        headless = config.selenium.modo_headless

    if headless:
        opciones.add_argument("--headless")
        opciones.add_argument("--window-size=1920,1080")
    else:
        # Abrir en pantalla completa cuando no es headless
        opciones.add_argument("--start-maximized")

    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--disable-extensions")
    opciones.add_argument("--disable-popup-blocking")

    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option("useAutomationExtension", False)

    try:
        _navegador = webdriver.Chrome(options=opciones)
        _navegador.implicitly_wait(config.selenium.tiempo_espera_implicito)

        # Maximizar ventana si no es headless
        if not headless:
            _navegador.maximize_window()

        logger.info("Navegador Chrome iniciado correctamente")
        logger.info(f"Modo headless: {headless}")
        logger.info(f"Tamaño de ventana: {'Maximizada' if not headless else '1920x1080'}")

        return _navegador

    except Exception as e:
        logger.error(f"Error al crear el navegador: {e}")
        raise


def obtener_navegador() -> Optional[webdriver.Chrome]:
    """
    Obtiene la instancia actual del navegador.

    Returns:
        Instancia del navegador o None si no existe
    """
    return _navegador


def establecer_zoom(zoom: int = 60) -> None:
    """
    Establece el nivel de zoom del navegador.

    Args:
        zoom: Porcentaje de zoom (por defecto 60% para capturas completas)
    """
    global _navegador

    if _navegador is None:
        logger.warning("No hay navegador activo para establecer zoom")
        return

    try:
        _navegador.execute_script(f"document.body.style.zoom='{zoom}%'")
        logger.info(f"Zoom establecido al {zoom}%")
    except Exception as e:
        logger.error(f"Error al establecer el zoom: {e}")


def cerrar_navegador() -> None:
    """Cierra el navegador y libera recursos."""
    global _navegador

    if _navegador is not None:
        try:
            _navegador.quit()
            logger.info("Navegador cerrado correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar el navegador: {e}")
        finally:
            _navegador = None


class NavegadorContextManager:
    """Context manager para manejar el navegador automáticamente."""

    def __init__(self, headless: Optional[bool] = None):
        self.headless = headless
        self.navegador = None

    def __enter__(self) -> webdriver.Chrome:
        self.navegador = crear_navegador(self.headless)
        return self.navegador

    def __exit__(self, exc_type, exc_val, exc_tb):
        cerrar_navegador()
        return False


def navegador_web(headless: Optional[bool] = None) -> NavegadorContextManager:
    """Función auxiliar para usar el context manager del navegador."""
    return NavegadorContextManager(headless)
