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
                logger.info(f"Directorio creado: {directorio}")

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

        logger.info("=" * 60)
        logger.info("INICIANDO PROCESO RPA - VERIFICACIÓN OFAC")
        logger.info("=" * 60)

        try:
            inicializar_pool()

            # Limpiar tabla de resultados para empezar con datos frescos
            logger.info("Limpiando tabla de resultados previa...")
            registros_eliminados = self.repo_resultados.limpiar_tabla()
            logger.info(f"✓ Tabla limpiada: {registros_eliminados} registros eliminados")
            logger.info("=" * 60)

            personas = self.repo_personas.obtener_personas_a_consultar()
            estadisticas['total_personas'] = len(personas)
            logger.info(f"Personas a procesar: {len(personas)}")

            if not personas:
                logger.warning("No hay personas para procesar")
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

            logger.info("=" * 60)
            logger.info("PROCESO COMPLETADO")
            logger.info(f"Estadísticas: {estadisticas}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error en el proceso principal: {e}")
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

            for persona in personas:
                try:
                    # Verificar si ya existe resultado para esta persona
                    if self.repo_resultados.existe_resultado_persona(persona.id_persona):
                        logger.warning(
                            f"Ya existe resultado para persona {persona.id_persona}. "
                            f"Se insertará un nuevo registro (no hay constraint UNIQUE)."
                        )

                    # Realizar búsqueda en OFAC
                    resultado_busqueda = buscador.buscar_persona(
                        nombre=persona.nombre_persona,
                        direccion=persona.direccion,
                        pais=persona.pais
                    )

                    # Clasificar según resultado de búsqueda
                    if resultado_busqueda.exito and resultado_busqueda.cantidad_resultados > 0:
                        # Búsqueda exitosa CON resultados → OK
                        # Capturar screenshot
                        try:
                            captura.capturar(id_persona=persona.id_persona)
                            logger.info(
                                f"Screenshot capturado para persona {persona.id_persona}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Error al capturar screenshot para persona {persona.id_persona}: {e}. "
                                f"Continuando con el guardado en BD."
                            )

                        estado = ESTADO_OK
                        stats['ok'] += 1
                        logger.info(
                            f"Persona {persona.id_persona}: OK - Cantidad encontrada: {resultado_busqueda.cantidad_resultados}"
                        )
                    else:
                        # Búsqueda sin resultados O error técnico → NOK
                        if resultado_busqueda.exito and resultado_busqueda.cantidad_resultados == 0:
                            # Búsqueda exitosa pero SIN resultados
                            logger.info(
                                f"Persona {persona.id_persona}: NOK - Búsqueda exitosa pero sin resultados (cantidad=0)"
                            )
                        else:
                            # Error técnico en la búsqueda
                            logger.warning(
                                f"Persona {persona.id_persona}: NOK - Búsqueda falló: "
                                f"{resultado_busqueda.mensaje_error}"
                            )

                        estado = ESTADO_NOK
                        stats['nok'] += 1

                    # Crear objeto Resultado
                    resultado = Resultado(
                        id_persona=persona.id_persona,
                        nombre_persona=persona.nombre_persona,
                        pais=persona.pais or "",
                        cantidad_resultados=resultado_busqueda.cantidad_resultados,
                        estado_transaccion=estado
                    )

                    # Validar campos obligatorios antes de insertar
                    if not self._validar_resultado(resultado):
                        logger.error(
                            f"Validación fallida para persona {persona.id_persona}. "
                            f"No se insertará en BD."
                        )
                        stats['errores'] += 1
                        continue

                    # Insertar resultado en BD
                    id_insertado = self.repo_resultados.insertar(resultado)
                    logger.info(
                        f"Resultado insertado con ID {id_insertado} para persona {persona.id_persona}: "
                        f"{estado}, cantidad={resultado_busqueda.cantidad_resultados}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error procesando persona {persona.id_persona}: {e}",
                        exc_info=True
                    )
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
        # Validar idPersona
        if not resultado.id_persona or resultado.id_persona <= 0:
            logger.error(f"idPersona es obligatorio y debe ser > 0: {resultado.id_persona}")
            return False

        # Validar nombrePersona
        if not resultado.nombre_persona or resultado.nombre_persona.strip() == "":
            logger.error(f"nombrePersona es obligatorio y no puede estar vacío")
            return False

        # Validar estadoTransaccion
        if not resultado.estado_transaccion or resultado.estado_transaccion.strip() == "":
            logger.error(f"estadoTransaccion es obligatorio y no puede estar vacío")
            return False

        return True
