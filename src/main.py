"""
Punto de entrada principal del bot RPA para verificación OFAC.
"""

import sys
import logging

from src.utilidades.logger import configurar_logging_global, escribir_resumen
from src.servicios import ServicioProcesamiento


def main():
    """Función principal que ejecuta el bot RPA."""
    configurar_logging_global(nivel=logging.WARNING)

    try:
        servicio = ServicioProcesamiento()
        estadisticas = servicio.ejecutar()

        print("\n" + "=" * 50)
        print("RESUMEN")
        print("=" * 50)
        print(f"  Total procesadas:    {estadisticas['total_personas']}")
        print(f"  OK:                  {estadisticas['procesadas_ok']}")
        print(f"  NOK:                 {estadisticas['procesadas_nok']}")
        print(f"  No cruzan maestra:   {estadisticas['no_cruzan_maestra']}")
        print(f"  Info incompleta:     {estadisticas['informacion_incompleta']}")
        print(f"  Errores:             {estadisticas['errores']}")
        print("=" * 50)

        ruta_resumen = escribir_resumen(estadisticas)
        print(f"\nResumen guardado en: {ruta_resumen}")

        return 0

    except KeyboardInterrupt:
        print("\nProceso interrumpido")
        return 1

    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
