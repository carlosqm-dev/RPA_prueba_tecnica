"""
Módulo de acceso a base de datos.
"""

from .conexion import obtener_conexion, cerrar_conexion
from .repositorio_personas import RepositorioPersonas
from .repositorio_resultados import RepositorioResultados
