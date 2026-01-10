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


def obtener_nombre_archivo_log() -> str:
    """
    Genera un nombre de archivo de log con timestamp.

    Returns:
        Nombre del archivo de log
    """
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"rpa_ofac_{fecha}.log"


def configurar_logging_global(nivel: int = logging.INFO) -> None:
    """
    Configura el logging global de la aplicación.

    Args:
        nivel: Nivel de logging
    """
    archivo_log = obtener_nombre_archivo_log()

    logging.basicConfig(
        level=nivel,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger_principal = configurar_logger(
        nombre="rpa_ofac",
        nivel=nivel,
        archivo_log=archivo_log
    )

    logger_principal.info(f"Logging configurado. Archivo: {archivo_log}")
