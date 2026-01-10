"""
Punto de entrada principal del bot RPA para verificación OFAC.
"""

import sys
import logging

from src.utilidades.logger import configurar_logging_global
from src.servicios import ServicioProcesamiento


def main():
    """Función principal que ejecuta el bot RPA."""
    configurar_logging_global(nivel=logging.INFO)
    logger = logging.getLogger("rpa_ofac")

    logger.info("=" * 60)
    logger.info("BOT RPA - VERIFICACIÓN DE SANCIONES OFAC")
    logger.info("=" * 60)

    try:
        servicio = ServicioProcesamiento()
        estadisticas = servicio.ejecutar()

        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DE EJECUCIÓN")
        logger.info("=" * 60)
        logger.info(f"  Total personas procesadas: {estadisticas['total_personas']}")
        logger.info(f"  Búsquedas exitosas (OK):   {estadisticas['procesadas_ok']}")
        logger.info(f"  Búsquedas fallidas (NOK):  {estadisticas['procesadas_nok']}")
        logger.info(f"  No cruzan con maestra:     {estadisticas['no_cruzan_maestra']}")
        logger.info(f"  Información incompleta:    {estadisticas['informacion_incompleta']}")
        logger.info(f"  Errores:                   {estadisticas['errores']}")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.warning("Proceso interrumpido por el usuario")
        return 1

    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
        logger.exception("Detalle del error:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
