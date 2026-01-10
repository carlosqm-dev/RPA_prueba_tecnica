"""
Servicio de validación de datos de personas.
"""

import logging
from typing import List, Tuple
from dataclasses import dataclass

from src.base_datos.repositorio_personas import Persona
from src.base_datos.repositorio_resultados import Resultado
from src.config.constantes import (
    ESTADO_INFORMACION_INCOMPLETA,
    ESTADO_NO_CRUZA_MAESTRA
)

logger = logging.getLogger(__name__)


@dataclass
class ResultadoValidacion:
    """Resultado de la validación de personas."""
    personas_validas: List[Persona]
    resultados_no_cruzan: List[Resultado]
    resultados_incompletos: List[Resultado]


class ServicioValidacion:
    """Servicio para validar datos de personas antes de consultar OFAC."""

    def clasificar_personas(self, personas: List[Persona]) -> ResultadoValidacion:
        """
        Clasifica las personas según la validez de sus datos.

        Args:
            personas: Lista de personas a clasificar

        Returns:
            ResultadoValidacion con las personas clasificadas
        """
        personas_validas = []
        resultados_no_cruzan = []
        resultados_incompletos = []

        for persona in personas:
            if self._no_cruza_con_maestra(persona):
                resultado = self._crear_resultado_no_cruza(persona)
                resultados_no_cruzan.append(resultado)
                logger.debug(
                    f"Persona {persona.id_persona} no cruza con maestra"
                )

            elif self._tiene_informacion_incompleta(persona):
                resultado = self._crear_resultado_incompleto(persona)
                resultados_incompletos.append(resultado)
                logger.debug(
                    f"Persona {persona.id_persona} tiene información incompleta"
                )

            else:
                personas_validas.append(persona)

        logger.info(
            f"Clasificación completada: "
            f"{len(personas_validas)} válidas, "
            f"{len(resultados_no_cruzan)} no cruzan, "
            f"{len(resultados_incompletos)} incompletas"
        )

        return ResultadoValidacion(
            personas_validas=personas_validas,
            resultados_no_cruzan=resultados_no_cruzan,
            resultados_incompletos=resultados_incompletos
        )

    def _no_cruza_con_maestra(self, persona: Persona) -> bool:
        """
        Verifica si la persona no tiene datos en la tabla maestra.

        Args:
            persona: Persona a verificar

        Returns:
            True si no tiene datos en maestra
        """
        return persona.direccion is None and persona.pais is None

    def _tiene_informacion_incompleta(self, persona: Persona) -> bool:
        """
        Verifica si la persona tiene información incompleta.

        Args:
            persona: Persona a verificar

        Returns:
            True si falta dirección o país
        """
        direccion_vacia = (
            persona.direccion is None or
            str(persona.direccion).strip() == ''
        )
        pais_vacio = (
            persona.pais is None or
            str(persona.pais).strip() == ''
        )

        return direccion_vacia or pais_vacio

    def _crear_resultado_no_cruza(self, persona: Persona) -> Resultado:
        """Crea un resultado para persona que no cruza con maestra."""
        return Resultado(
            id_persona=persona.id_persona,
            nombre_persona=persona.nombre_persona,
            pais="",
            cantidad_resultados=0,
            estado_transaccion=ESTADO_NO_CRUZA_MAESTRA
        )

    def _crear_resultado_incompleto(self, persona: Persona) -> Resultado:
        """Crea un resultado para persona con información incompleta."""
        return Resultado(
            id_persona=persona.id_persona,
            nombre_persona=persona.nombre_persona,
            pais=persona.pais or "",
            cantidad_resultados=0,
            estado_transaccion=ESTADO_INFORMACION_INCOMPLETA
        )
