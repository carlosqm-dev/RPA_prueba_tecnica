"""
Módulo de conexión a la base de datos PostgreSQL.
Implementa un pool de conexiones para mejor rendimiento.
"""

import psycopg2
from psycopg2 import pool, Error
from typing import Optional
import logging

from src.config import Configuracion

logger = logging.getLogger(__name__)

_pool_conexiones: Optional[pool.SimpleConnectionPool] = None


def inicializar_pool(min_conexiones: int = 1, max_conexiones: int = 10) -> None:
    """
    Inicializa el pool de conexiones a la base de datos.

    Args:
        min_conexiones: Número mínimo de conexiones en el pool
        max_conexiones: Número máximo de conexiones en el pool
    """
    global _pool_conexiones

    if _pool_conexiones is not None:
        return

    try:
        config = Configuracion()
        _pool_conexiones = pool.SimpleConnectionPool(
            min_conexiones,
            max_conexiones,
            host=config.base_datos.host,
            port=config.base_datos.puerto,
            database=config.base_datos.base_datos,
            user=config.base_datos.usuario,
            password=config.base_datos.contrasena
        )
    except Error as e:
        logger.error(f"Error al inicializar pool de conexiones: {e}")
        raise


def obtener_conexion():
    """
    Obtiene una conexión del pool.

    Returns:
        Conexión a la base de datos

    Raises:
        Exception: Si el pool no está inicializado
    """
    global _pool_conexiones

    if _pool_conexiones is None:
        inicializar_pool()

    try:
        conexion = _pool_conexiones.getconn()
        return conexion
    except Error as e:
        logger.error(f"Error al obtener conexión: {e}")
        raise


def cerrar_conexion(conexion) -> None:
    """
    Devuelve una conexión al pool.

    Args:
        conexion: Conexión a devolver al pool
    """
    global _pool_conexiones

    if _pool_conexiones is not None and conexion is not None:
        _pool_conexiones.putconn(conexion)


def cerrar_pool() -> None:
    """Cierra todas las conexiones del pool."""
    global _pool_conexiones

    if _pool_conexiones is not None:
        _pool_conexiones.closeall()
        _pool_conexiones = None


class ConexionContextManager:
    """Context manager para manejar conexiones automáticamente."""

    def __init__(self):
        self.conexion = None

    def __enter__(self):
        self.conexion = obtener_conexion()
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conexion:
            if exc_type is not None:
                self.conexion.rollback()
            cerrar_conexion(self.conexion)
        return False


def conexion_bd():
    """Función auxiliar para usar el context manager."""
    return ConexionContextManager()
