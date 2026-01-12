"""
Configuración del sistema de logging.
"""

import logging
import os
from datetime import datetime
from typing import Optional

from src.config import Configuracion


def configurar_logger(
    nombre: str = "rpa_ofac",
    nivel: int = logging.INFO,
    archivo_log: Optional[str] = None
) -> logging.Logger:
    """
    Configura y retorna un logger con handlers para consola y archivo.

    Args:
        nombre: Nombre del logger
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        archivo_log: Nombre del archivo de log (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)

    if logger.handlers:
        return logger

    formato = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel)
    handler_consola.setFormatter(formato)
    logger.addHandler(handler_consola)

    if archivo_log:
        config = Configuracion()
        directorio_logs = config.directorio_logs

        if not os.path.exists(directorio_logs):
            os.makedirs(directorio_logs)

        ruta_log = os.path.join(directorio_logs, archivo_log)
        handler_archivo = logging.FileHandler(ruta_log, encoding='utf-8')
        handler_archivo.setLevel(nivel)
        handler_archivo.setFormatter(formato)
        logger.addHandler(handler_archivo)

    return logger


def obtener_nombre_archivo_resumen() -> str:
    """
    Genera el nombre del archivo de resumen con fecha de hoy.

    Returns:
        Nombre del archivo de resumen
    """
    fecha = datetime.now().strftime("%Y%m%d")
    return f"resumen_rpa_ofac_{fecha}.log"


def escribir_resumen(estadisticas: dict) -> str:
    """
    Escribe el resumen del proceso en un archivo de log.

    Args:
        estadisticas: Diccionario con las estadísticas del proceso

    Returns:
        Ruta del archivo de resumen creado
    """
    config = Configuracion()
    directorio_logs = config.directorio_logs

    if not os.path.exists(directorio_logs):
        os.makedirs(directorio_logs)

    nombre_archivo = obtener_nombre_archivo_resumen()
    ruta_resumen = os.path.join(directorio_logs, nombre_archivo)

    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contenido = f"""
{'=' * 60}
RESUMEN DE EJECUCIÓN RPA OFAC
{'=' * 60}
Fecha y hora: {fecha_hora}
{'=' * 60}

ESTADÍSTICAS:
  - Total personas procesadas:  {estadisticas.get('total_personas', 0)}
  - Búsquedas exitosas (OK):    {estadisticas.get('procesadas_ok', 0)}
  - Búsquedas fallidas (NOK):   {estadisticas.get('procesadas_nok', 0)}
  - No cruzan con maestra:      {estadisticas.get('no_cruzan_maestra', 0)}
  - Información incompleta:     {estadisticas.get('informacion_incompleta', 0)}
  - Errores:                    {estadisticas.get('errores', 0)}

{'=' * 60}
FIN DEL RESUMEN
{'=' * 60}
"""

    with open(ruta_resumen, 'a', encoding='utf-8') as archivo:
        archivo.write(contenido)

    return ruta_resumen


def configurar_logging_global(nivel: int = logging.INFO) -> None:
    """
    Configura el logging global de la aplicación.

    Args:
        nivel: Nivel de logging
    """
    logging.basicConfig(
        level=nivel,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
