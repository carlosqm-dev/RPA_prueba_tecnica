"""
Repositorio para operaciones CRUD de la tabla de Resultados.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

import pandas as pd

from src.config.constantes import TABLA_RESULTADOS
from .conexion import conexion_bd

logger = logging.getLogger(__name__)


@dataclass
class Resultado:
    """Modelo de datos para un resultado de búsqueda OFAC."""
    id: Optional[int] = None
    id_persona: int = 0
    nombre_persona: str = ""
    pais: str = ""
    cantidad_resultados: int = 0
    estado_transaccion: str = ""


class RepositorioResultados:
    """Repositorio para acceder a datos de resultados."""

    def insertar(self, resultado: Resultado) -> int:
        """
        Inserta un nuevo resultado en la base de datos.

        Args:
            resultado: Objeto Resultado a insertar

        Returns:
            ID del registro insertado
        """
        query = f"""
            INSERT INTO {TABLA_RESULTADOS}
            ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        try:
            with conexion_bd() as conexion:
                cursor = conexion.cursor()
                cursor.execute(query, (
                    resultado.id_persona,
                    resultado.nombre_persona,
                    resultado.pais,
                    resultado.cantidad_resultados,
                    resultado.estado_transaccion
                ))
                id_insertado = cursor.fetchone()[0]
                conexion.commit()
                cursor.close()

            logger.info(
                f"Resultado insertado para persona {resultado.id_persona}: "
                f"{resultado.estado_transaccion}"
            )
            return id_insertado

        except Exception as e:
            logger.error(f"Error al insertar resultado: {e}")
            raise

    def insertar_lote(self, resultados: List[Resultado]) -> int:
        """
        Inserta múltiples resultados en una sola operación.

        Args:
            resultados: Lista de objetos Resultado a insertar

        Returns:
            Número de registros insertados
        """
        if not resultados:
            return 0

        query = f"""
            INSERT INTO {TABLA_RESULTADOS}
            ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
            VALUES (%s, %s, %s, %s, %s)
        """

        try:
            with conexion_bd() as conexion:
                cursor = conexion.cursor()
                datos = [
                    (
                        r.id_persona,
                        r.nombre_persona,
                        r.pais,
                        r.cantidad_resultados,
                        r.estado_transaccion
                    )
                    for r in resultados
                ]
                cursor.executemany(query, datos)
                conexion.commit()
                registros_insertados = cursor.rowcount
                cursor.close()

            logger.info(f"Se insertaron {registros_insertados} resultados en lote")
            return registros_insertados

        except Exception as e:
            logger.error(f"Error al insertar resultados en lote: {e}")
            raise

    def obtener_por_estado(self, estado: str) -> List[Resultado]:
        """
        Obtiene todos los resultados con un estado específico.

        Args:
            estado: Estado de transacción a filtrar

        Returns:
            Lista de objetos Resultado
        """
        query = f"""
            SELECT id, "idPersona", "nombrePersona", "pais",
                   "cantidadDeResultados", "estadoTransaccion"
            FROM {TABLA_RESULTADOS}
            WHERE "estadoTransaccion" = %s
        """

        try:
            with conexion_bd() as conexion:
                df = pd.read_sql_query(query, conexion, params=(estado,))

            resultados = []
            for _, row in df.iterrows():
                resultado = Resultado(
                    id=row['id'],
                    id_persona=row['idPersona'],
                    nombre_persona=row['nombrePersona'],
                    pais=row['pais'],
                    cantidad_resultados=row['cantidadDeResultados'],
                    estado_transaccion=row['estadoTransaccion']
                )
                resultados.append(resultado)

            return resultados

        except Exception as e:
            logger.error(f"Error al obtener resultados por estado {estado}: {e}")
            raise

    def existe_resultado_persona(self, id_persona: int) -> bool:
        """
        Verifica si ya existe un resultado para una persona.

        Args:
            id_persona: ID de la persona a verificar

        Returns:
            True si existe, False en caso contrario
        """
        query = f"""
            SELECT COUNT(*)
            FROM {TABLA_RESULTADOS}
            WHERE "idPersona" = %s
        """

        try:
            with conexion_bd() as conexion:
                cursor = conexion.cursor()
                cursor.execute(query, (id_persona,))
                count = cursor.fetchone()[0]
                cursor.close()

            return count > 0

        except Exception as e:
            logger.error(f"Error al verificar resultado para persona {id_persona}: {e}")
            raise

    def obtener_todos(self) -> pd.DataFrame:
        """
        Obtiene todos los resultados como DataFrame.

        Returns:
            DataFrame con todos los resultados
        """
        query = f"SELECT * FROM {TABLA_RESULTADOS}"

        try:
            with conexion_bd() as conexion:
                df = pd.read_sql_query(query, conexion)
            return df

        except Exception as e:
            logger.error(f"Error al obtener todos los resultados: {e}")
            raise
