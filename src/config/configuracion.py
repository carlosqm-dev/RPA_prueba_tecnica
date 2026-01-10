"""
Configuración centralizada del proyecto.
Carga variables de entorno y proporciona acceso a la configuración.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfiguracionBaseDatos:
    """Configuración de conexión a la base de datos."""
    host: str
    puerto: str
    base_datos: str
    usuario: str
    contrasena: str

    @property
    def url_conexion(self) -> str:
        """Retorna la URL de conexión completa."""
        return (
            f"postgresql://{self.usuario}:{self.contrasena}"
            f"@{self.host}:{self.puerto}/{self.base_datos}"
        )


@dataclass
class ConfiguracionSelenium:
    """Configuración para el navegador Selenium."""
    url_ofac: str = "https://sanctionssearch.ofac.treas.gov/"
    tiempo_espera_implicito: int = 10
    tiempo_espera_explicito: int = 20
    modo_headless: bool = False


class Configuracion:
    """Clase principal de configuración que carga valores del entorno."""

    _instancia: Optional['Configuracion'] = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        """Inicializa la configuración cargando variables de entorno."""
        self.base_datos = ConfiguracionBaseDatos(
            host=os.getenv(
                'DB_HOST',
                'rpa-prevalentware.c3rkad1ay1ao.us-east-1.rds.amazonaws.com'
            ),
            puerto=os.getenv('DB_PORT', '5432'),
            base_datos=os.getenv('DB_NAME', 'prueba-tecnica'),
            usuario=os.getenv('DB_USER', 'user9145'),
            contrasena=os.getenv('DB_PASSWORD', 'pruebauser91452023')
        )

        self.selenium = ConfiguracionSelenium(
            url_ofac=os.getenv(
                'OFAC_URL',
                'https://sanctionssearch.ofac.treas.gov/'
            ),
            tiempo_espera_implicito=int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10')),
            tiempo_espera_explicito=int(os.getenv('SELENIUM_EXPLICIT_WAIT', '20')),
            modo_headless=os.getenv('SELENIUM_HEADLESS', 'false').lower() == 'true'
        )

        self.directorio_capturas = os.getenv('DIR_CAPTURAS', 'capturas')
        self.directorio_reportes = os.getenv('DIR_REPORTES', 'reportes')
        self.directorio_logs = os.getenv('DIR_LOGS', 'logs')


def obtener_configuracion() -> Configuracion:
    """Función auxiliar para obtener la instancia de configuración."""
    return Configuracion()
