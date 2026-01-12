"""
Servicio principal de procesamiento del bot RPA.
Orquesta todas las operaciones del flujo de trabajo.
"""

import logging
import os
from datetime import datetime
from typing import Optional

from src.config import Configuracion
from src.config.constantes import (
    ESTADO_OK,
    ESTADO_NOK,
    FORMATO_FECHA_CAPTURA,
    FORMATO_NOMBRE_CAPTURA
)
from src.base_datos import RepositorioPersonas, RepositorioResultados
from src.base_datos.repositorio_resultados import Resultado
from src.base_datos.conexion import inicializar_pool, cerrar_pool
from src.scraping import BuscadorOfac
from src.scraping.navegador import navegador_web
from src.utilidades.captura_pantalla import CapturaPantalla
from .servicio_validacion import ServicioValidacion
from .servicio_exportacion import ServicioExportacion

logger = logging.getLogger(__name__)


class ServicioProcesamiento:
    """Servicio orquestador del proceso RPA."""

    def __init__(self):
        """Inicializa el servicio de procesamiento."""
        self.config = Configuracion()
        self.repo_personas = RepositorioPersonas()
        self.repo_resultados = RepositorioResultados()
        self.servicio_validacion = ServicioValidacion()
        self.servicio_exportacion = ServicioExportacion()

        self._crear_directorios()

    def _crear_directorios(self) -> None:
        """Crea los directorios necesarios si no existen."""
        directorios = [
            self.config.directorio_capturas,
            self.config.directorio_reportes,
            self.config.directorio_logs
        ]

        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)

    def ejecutar(self) -> dict:
        """
        Ejecuta el proceso completo del bot RPA.

        Returns:
            Diccionario con estadísticas del proceso
        """
        estadisticas = {
            'total_personas': 0,
            'procesadas_ok': 0,
            'procesadas_nok': 0,
            'no_cruzan_maestra': 0,
            'informacion_incompleta': 0,
            'errores': 0
        }

        print("\n" + "=" * 50)
        print("BOT RPA - VERIFICACIÓN OFAC")
        print("=" * 50)

        try:
            inicializar_pool()
            self.repo_resultados.limpiar_tabla()

            personas = self.repo_personas.obtener_personas_a_consultar()
            estadisticas['total_personas'] = len(personas)
            print(f"Personas a procesar: {len(personas)}")

            if not personas:
                print("No hay personas para procesar")
                return estadisticas

            resultado_validacion = self.servicio_validacion.clasificar_personas(
                personas
            )

            if resultado_validacion.resultados_no_cruzan:
                self.repo_resultados.insertar_lote(
                    resultado_validacion.resultados_no_cruzan
                )
                estadisticas['no_cruzan_maestra'] = len(
                    resultado_validacion.resultados_no_cruzan
                )

            if resultado_validacion.resultados_incompletos:
                self.repo_resultados.insertar_lote(
                    resultado_validacion.resultados_incompletos
                )
                estadisticas['informacion_incompleta'] = len(
                    resultado_validacion.resultados_incompletos
                )

            if resultado_validacion.personas_validas:
                stats_ofac = self._procesar_busquedas_ofac(
                    resultado_validacion.personas_validas
                )
                estadisticas['procesadas_ok'] = stats_ofac['ok']
                estadisticas['procesadas_nok'] = stats_ofac['nok']
                estadisticas['errores'] = stats_ofac['errores']

            self.servicio_exportacion.exportar_incompletos()

        except Exception as e:
            logger.error(f"Error en proceso principal: {e}")
            raise

        finally:
            cerrar_pool()

        return estadisticas

    def _procesar_busquedas_ofac(self, personas: list) -> dict:
        """
        Procesa las búsquedas OFAC para las personas válidas.

        Args:
            personas: Lista de personas a buscar en OFAC

        Returns:
            Diccionario con contadores de resultados
        """
        stats = {'ok': 0, 'nok': 0, 'errores': 0}

        with navegador_web() as navegador:
            buscador = BuscadorOfac(navegador)
            captura = CapturaPantalla(navegador)

            if not buscador.navegar_a_ofac():
                logger.error("No se pudo acceder al sitio OFAC")
                stats['errores'] = len(personas)
                return stats

            for i, persona in enumerate(personas, 1):
                try:
                    print(f"  [{i}/{len(personas)}] {persona.nombre_persona}...", end=" ")

                    # Realizar búsqueda en OFAC
                    resultado_busqueda = buscador.buscar_persona(
                        nombre=persona.nombre_persona,
                        direccion=persona.direccion,
                        pais=persona.pais
                    )

                    if resultado_busqueda.exito and resultado_busqueda.cantidad_resultados > 0:
                        try:
                            captura.capturar(id_persona=persona.id_persona)
                        except Exception:
                            pass
                        estado = ESTADO_OK
                        stats['ok'] += 1
                        print(f"OK ({resultado_busqueda.cantidad_resultados} resultados)")
                    else:
                        estado = ESTADO_NOK
                        stats['nok'] += 1
                        print("NOK")

                    resultado = Resultado(
                        id_persona=persona.id_persona,
                        nombre_persona=persona.nombre_persona,
                        pais=persona.pais or "",
                        cantidad_resultados=resultado_busqueda.cantidad_resultados,
                        estado_transaccion=estado
                    )

                    if not self._validar_resultado(resultado):
                        stats['errores'] += 1
                        continue

                    self.repo_resultados.insertar(resultado)

                except Exception as e:
                    print(f"ERROR")
                    logger.error(f"Error procesando persona {persona.id_persona}: {e}")
                    stats['errores'] += 1

        return stats

    def _validar_resultado(self, resultado: Resultado) -> bool:
        """
        Valida que un resultado tenga los campos obligatorios.

        Args:
            resultado: Objeto Resultado a validar

        Returns:
            True si es válido, False en caso contrario
        """
        if not resultado.id_persona or resultado.id_persona <= 0:
            return False
        if not resultado.nombre_persona or resultado.nombre_persona.strip() == "":
            return False
        if not resultado.estado_transaccion or resultado.estado_transaccion.strip() == "":
            return False
        return True
