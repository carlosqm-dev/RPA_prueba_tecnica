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

        Returns:
            Ruta del archivo Excel generado
        """
        try:
            resultados = self.repo_resultados.obtener_por_estado(
                ESTADO_INFORMACION_INCOMPLETA
            )

            if not resultados:
                logger.info("No hay registros incompletos para exportar")
                return ""

            datos = [
                {
                    'ID Persona': r.id_persona,
                    'Nombre': r.nombre_persona,
                    'País': r.pais,
                    'Cantidad Resultados': r.cantidad_resultados,
                    'Estado': r.estado_transaccion
                }
                for r in resultados
            ]

            df = pd.DataFrame(datos)

            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = FORMATO_NOMBRE_REPORTE.format(fecha=fecha)
            ruta_completa = os.path.join(
                self.config.directorio_reportes,
                nombre_archivo
            )

            df.to_excel(ruta_completa, index=False, sheet_name='Incompletos')

            logger.info(
                f"Reporte exportado: {ruta_completa} "
                f"({len(resultados)} registros)"
            )

            return ruta_completa

        except Exception as e:
            logger.error(f"Error al exportar a Excel: {e}")
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
                logger.info("No hay resultados para exportar")
                return ""

            if nombre_archivo is None:
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"resultados_completos_{fecha}.xlsx"

            ruta_completa = os.path.join(
                self.config.directorio_reportes,
                nombre_archivo
            )

            df.to_excel(ruta_completa, index=False, sheet_name='Resultados')

            logger.info(
                f"Resultados exportados: {ruta_completa} "
                f"({len(df)} registros)"
            )

            return ruta_completa

        except Exception as e:
            logger.error(f"Error al exportar resultados: {e}")
            raise
