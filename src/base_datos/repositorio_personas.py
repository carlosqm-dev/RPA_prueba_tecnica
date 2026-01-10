"""
Repositorio para operaciones CRUD de la tabla Personas.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

import pandas as pd

from src.config.constantes import (
    TABLA_PERSONAS,
    TABLA_MAESTRA,
    CONSULTAR_SI
)
from .conexion import conexion_bd

logger = logging.getLogger(__name__)


@dataclass
class Persona:
    """Modelo de datos para una persona."""
    id: int
    id_persona: int
    nombre_persona: str
    a_consultar: str
    direccion: Optional[str] = None
    pais: Optional[str] = None


class RepositorioPersonas:
    """Repositorio para acceder a datos de personas."""

    def obtener_personas_a_consultar(self) -> List[Persona]:
        """
        Obtiene las personas que deben ser consultadas en OFAC.

        Returns:
            Lista de objetos Persona con aConsultar = 'Si'
        """
        query = f"""
            SELECT
                p.id,
                p."idPersona",
                p."nombrePersona",
                p."aConsultar",
                m.direccion,
                m.pais
            FROM {TABLA_PERSONAS} p
            LEFT JOIN {TABLA_MAESTRA} m ON p."idPersona" = m."idPersona"
            WHERE p."aConsultar" = %s
        """

        try:
            with conexion_bd() as conexion:
                df = pd.read_sql_query(query, conexion, params=(CONSULTAR_SI,))

            personas = []
            for _, row in df.iterrows():
                persona = Persona(
                    id=row['id'],
                    id_persona=row['idPersona'],
                    nombre_persona=row['nombrePersona'],
                    a_consultar=row['aConsultar'],
                    direccion=row.get('direccion'),
                    pais=row.get('pais')
                )
                personas.append(persona)

            logger.info(f"Se obtuvieron {len(personas)} personas a consultar")
            return personas

        except Exception as e:
            logger.error(f"Error al obtener personas a consultar: {e}")
            raise

    def obtener_persona_por_id(self, id_persona: int) -> Optional[Persona]:
        """
        Obtiene una persona específica por su idPersona.

        Args:
            id_persona: ID de la persona a buscar

        Returns:
            Objeto Persona o None si no existe
        """
        query = f"""
            SELECT
                p.id,
                p."idPersona",
                p."nombrePersona",
                p."aConsultar",
                m.direccion,
                m.pais
            FROM {TABLA_PERSONAS} p
            LEFT JOIN {TABLA_MAESTRA} m ON p."idPersona" = m."idPersona"
            WHERE p."idPersona" = %s
        """

        try:
            with conexion_bd() as conexion:
                cursor = conexion.cursor()
                cursor.execute(query, (id_persona,))
                row = cursor.fetchone()
                cursor.close()

            if row:
                return Persona(
                    id=row[0],
                    id_persona=row[1],
                    nombre_persona=row[2],
                    a_consultar=row[3],
                    direccion=row[4],
                    pais=row[5]
                )
            return None

        except Exception as e:
            logger.error(f"Error al obtener persona {id_persona}: {e}")
            raise

    def contar_personas_a_consultar(self) -> int:
        """
        Cuenta el número de personas pendientes de consultar.

        Returns:
            Número de personas con aConsultar = 'Si'
        """
        query = f"""
            SELECT COUNT(*)
            FROM {TABLA_PERSONAS}
            WHERE "aConsultar" = %s
        """

        try:
            with conexion_bd() as conexion:
                cursor = conexion.cursor()
                cursor.execute(query, (CONSULTAR_SI,))
                count = cursor.fetchone()[0]
                cursor.close()

            return count

        except Exception as e:
            logger.error(f"Error al contar personas: {e}")
            raise
