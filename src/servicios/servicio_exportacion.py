"""
Servicio de exportación de datos a Excel.
"""

import logging
import os
from datetime import datetime

import pandas as pd

from src.config import Configuracion
from src.config.constantes import (
    ESTADO_INFORMACION_INCOMPLETA,
    FORMATO_NOMBRE_REPORTE
)
from src.base_datos import RepositorioResultados

logger = logging.getLogger(__name__)


class ServicioExportacion:
    """Servicio para exportar datos a archivos Excel."""

    def __init__(self):
        """Inicializa el servicio de exportación."""
        self.config = Configuracion()
        self.repo_resultados = RepositorioResultados()

    def exportar_incompletos(self) -> str:
        """
        Exporta los registros con información incompleta a Excel.
        Incluye el campo dirección de la tabla MaestraDetallePersonas.

        Returns:
            Ruta del archivo Excel generado o cadena vacía si no hay registros
        """
        try:
            # Obtener DataFrame con dirección incluida
            df = self.repo_resultados.obtener_incompletos_con_direccion()

            if df.empty:
                return ""

            # Crear directorio de reportes si no existe
            os.makedirs(self.config.directorio_reportes, exist_ok=True)

            # Generar nombre del archivo con formato YYYYMMDD
            fecha = datetime.now().strftime("%Y%m%d")
            nombre_archivo = FORMATO_NOMBRE_REPORTE.format(fecha=fecha)
            ruta_completa = os.path.join(
                self.config.directorio_reportes,
                nombre_archivo
            )

            # Exportar a Excel usando openpyxl
            df.to_excel(ruta_completa, index=False, engine='openpyxl', sheet_name='Incompletos')

            print(f"Reporte exportado: {ruta_completa}")
            return ruta_completa

        except Exception as e:
            logger.error(f"Error al exportar: {e}")
            raise

    def exportar_todos_los_resultados(self, nombre_archivo: str = None) -> str:
        """
        Exporta todos los resultados a un archivo Excel.

        Args:
            nombre_archivo: Nombre del archivo (opcional)

        Returns:
            Ruta del archivo Excel generado
        """
        try:
            df = self.repo_resultados.obtener_todos()

            if df.empty:
                return ""

            if nombre_archivo is None:
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"resultados_completos_{fecha}.xlsx"

            ruta_completa = os.path.join(
                self.config.directorio_reportes,
                nombre_archivo
            )

            df.to_excel(ruta_completa, index=False, sheet_name='Resultados')

            return ruta_completa

        except Exception as e:
            logger.error(f"Error al exportar: {e}")
            raise
