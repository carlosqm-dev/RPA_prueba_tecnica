"""
Prueba HU-08: Capturar Screenshot de Resultados
Este test valida:
1. Obtener personas con información COMPLETA desde la base de datos
2. Buscar cada persona en OFAC
3. Capturar screenshot cuando hay resultados > 0
4. NO capturar screenshot cuando no hay resultados (cantidad = 0)
5. Guardar con el formato correcto: YYYYMMDD_idPersona.png
6. Crear directorio 'capturas/' si no existe
7. Manejar errores al capturar screenshots
8. Continuar el proceso aunque falle la captura

NOTA: Este test NO guarda nada en la tabla Resultadosuser9145.
      Solo muestra información por consola y guarda screenshots.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import os
import time
import psycopg2
from datetime import datetime
from typing import Optional, List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.utilidades.captura_pantalla import CapturaPantalla
from src.scraping.buscador_ofac import BuscadorOfac
from src.config.constantes import FORMATO_FECHA_CAPTURA, FORMATO_NOMBRE_CAPTURA


# ========================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ========================================================================

DB_CONFIG = {
    'host': 'rpa-prevalentware.c3rkad1ay1ao.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'database': 'prueba-tecnica',
    'user': 'user9145',
    'password': 'pruebauser91452023'
}


# ========================================================================
# FUNCIONES DE BASE DE DATOS
# ========================================================================

def conectar_base_datos():
    """Conecta a la base de datos PostgreSQL."""
    try:
        connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return connection
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None


def obtener_personas_validas(connection) -> List[Dict]:
    """
    Obtiene todas las personas con información COMPLETA desde la base de datos.

    Una persona tiene información completa si:
    - Está en la tabla Personas con aConsultar = 'Si'
    - Tiene registro en MaestraDetallePersonas
    - Tiene dirección válida (no NULL, no vacío, no 'None')
    - Tiene país válido (no NULL, no vacío, no 'None')

    Returns:
        Lista de diccionarios con los datos de las personas válidas
    """
    query = """
    SELECT
        p."idPersona",
        p."nombrePersona",
        m.direccion,
        m.pais
    FROM "Personas" p
    INNER JOIN "MaestraDetallePersonas" m ON p."idPersona" = m."idPersona"
    WHERE p."aConsultar" = 'Si'
        AND m.direccion IS NOT NULL
        AND m.direccion != 'None'
        AND m.direccion != ''
        AND m.pais IS NOT NULL
        AND m.pais != 'None'
        AND m.pais != ''
    ORDER BY p."idPersona"
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        personas = []
        for row in resultados:
            persona = {
                'idPersona': row[0],
                'nombrePersona': row[1],
                'direccion': row[2],
                'pais': row[3]
            }
            personas.append(persona)

        return personas

    except Exception as e:
        print(f"[ERROR] Error al consultar la base de datos: {e}")
        return []


# ========================================================================
# FUNCIONES DE UTILIDAD
# ========================================================================

def configurar_navegador(headless: bool = False) -> webdriver.Chrome:
    """
    Configura y retorna una instancia del navegador Chrome.

    Args:
        headless: Si es True, ejecuta el navegador sin interfaz gráfica

    Returns:
        Instancia de Chrome WebDriver
    """
    opciones = Options()
    if headless:
        opciones.add_argument('--headless')
    else:
        # Abrir en modo maximizado para capturas completas
        opciones.add_argument('--start-maximized')

    opciones.add_argument('--disable-gpu')
    opciones.add_argument('--no-sandbox')
    opciones.add_argument('--disable-dev-shm-usage')

    # Si es headless, establecer tamaño de ventana grande
    if headless:
        opciones.add_argument('--window-size=1920,1080')

    servicio = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servicio, options=opciones)

    # Si no es headless, maximizar la ventana
    if not headless:
        navegador.maximize_window()

    return navegador


def establecer_zoom_navegador(navegador: webdriver.Chrome, zoom: int = 60):
    """
    Establece el nivel de zoom del navegador.

    Args:
        navegador: Instancia del navegador Chrome
        zoom: Porcentaje de zoom (por defecto 60%)
    """
    try:
        navegador.execute_script(f"document.body.style.zoom='{zoom}%'")
        print(f"  ✓ Zoom establecido al {zoom}%")
    except Exception as e:
        print(f"  ⚠️  No se pudo establecer el zoom: {e}")


def mostrar_encabezado():
    """Muestra el encabezado del test."""
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 15 + "TEST HU-08: CAPTURA DE SCREENSHOTS" + " " * 27 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()
    print("Este test:")
    print("  1. Obtiene personas con información COMPLETA desde la BD")
    print("  2. Busca cada persona en OFAC")
    print("  3. Captura screenshot cuando cantidad > 0")
    print("  4. NO captura screenshot cuando cantidad = 0")
    print("  5. Formato del nombre: YYYYMMDD_idPersona.png")
    print("  6. Crea directorio 'capturas/' si no existe")
    print("  7. Maneja errores al capturar")
    print()
    print("CONFIGURACIÓN:")
    print("  - Navegador en pantalla completa (maximizado)")
    print("  - Zoom al 60% para capturas completas")
    print()
    print("IMPORTANTE: Este test NO guarda nada en la tabla Resultadosuser9145.")
    print("            Solo muestra información y guarda screenshots.")
    print()


def mostrar_listado_personas(personas: List[Dict]):
    """Muestra el listado de personas obtenidas de la BD."""
    print()
    print("=" * 80)
    print("PERSONAS CON INFORMACIÓN COMPLETA")
    print("=" * 80)
    print(f"Total de personas a procesar: {len(personas)}")
    print()

    if not personas:
        print("  ⚠️  No hay personas con información completa para procesar")
        return

    # Mostrar las primeras 10, luego resumir
    limite_mostrar = 10

    for idx, persona in enumerate(personas[:limite_mostrar], 1):
        print(f"{idx:2}. ID: {persona['idPersona']:3} | {persona['nombrePersona']}")
        print(f"    Dirección: {persona['direccion']}")
        print(f"    País:      {persona['pais']}")
        print()

    if len(personas) > limite_mostrar:
        print(f"    ... y {len(personas) - limite_mostrar} personas más")
        print()

    print("=" * 80)


def mostrar_persona(persona: dict, numero: int, total: int):
    """Muestra la información de la persona que se va a procesar."""
    print()
    print("=" * 80)
    print(f"PROCESANDO PERSONA {numero}/{total}")
    print("=" * 80)
    print(f"  ID Persona: {persona['idPersona']}")
    print(f"  Nombre:     {persona['nombrePersona']}")
    print(f"  Dirección:  {persona['direccion']}")
    print(f"  País:       {persona['pais']}")
    print("-" * 80)


def mostrar_resultado_busqueda(cantidad: int):
    """Muestra el resultado de la búsqueda."""
    print()
    print(f"  [RESULTADO] Cantidad encontrada: {cantidad}")

    if cantidad > 0:
        print(f"  [ACCIÓN] Se debe capturar screenshot")
    else:
        print(f"  [ACCIÓN] NO se debe capturar screenshot (cantidad = 0)")


def mostrar_captura_exitosa(ruta: str, id_persona: int):
    """Muestra información de una captura exitosa."""
    fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
    nombre_esperado = FORMATO_NOMBRE_CAPTURA.format(
        fecha=fecha_actual,
        id_persona=id_persona
    )

    print()
    print(f"  ✓ [CAPTURA EXITOSA]")
    print(f"    Archivo:         {os.path.basename(ruta)}")
    print(f"    Ruta completa:   {ruta}")
    print(f"    Formato esperado: {nombre_esperado}")
    print(f"    ¿Coincide?:      {'SÍ' if os.path.basename(ruta) == nombre_esperado else 'NO'}")

    # Verificar que el archivo existe
    if os.path.exists(ruta):
        tamaño = os.path.getsize(ruta)
        print(f"    Tamaño:          {tamaño} bytes")
    else:
        print(f"    ⚠️  ERROR: El archivo no existe")


def mostrar_sin_captura(motivo: str):
    """Muestra información cuando no se captura screenshot."""
    print()
    print(f"  ⊗ [SIN CAPTURA]")
    print(f"    Motivo: {motivo}")


def mostrar_error_captura(error: str):
    """Muestra información de error al capturar."""
    print()
    print(f"  ✗ [ERROR AL CAPTURAR]")
    print(f"    Error: {error}")
    print(f"    ⚠️  El proceso debe continuar (no debe detenerse)")


def verificar_directorio_capturas():
    """Verifica que el directorio de capturas exista."""
    directorio = "capturas"

    print()
    print("=" * 80)
    print("VERIFICACIÓN DE DIRECTORIO")
    print("=" * 80)

    if os.path.exists(directorio):
        print(f"  ✓ Directorio '{directorio}/' ya existe")

        # Listar capturas existentes
        archivos = [f for f in os.listdir(directorio) if f.endswith('.png')]
        if archivos:
            print(f"  ℹ️  Archivos existentes: {len(archivos)}")
            for archivo in archivos[:5]:  # Mostrar solo los primeros 5
                print(f"    - {archivo}")
            if len(archivos) > 5:
                print(f"    ... y {len(archivos) - 5} más")
    else:
        print(f"  ℹ️  Directorio '{directorio}/' no existe")
        print(f"  ➜ Se creará automáticamente al capturar")

    print()


def mostrar_resumen_final(resultados: list):
    """Muestra el resumen final del test."""
    print()
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)

    total = len(resultados)
    con_resultados = sum(1 for r in resultados if r['cantidad'] > 0)
    sin_resultados = sum(1 for r in resultados if r['cantidad'] == 0)
    capturas_exitosas = sum(1 for r in resultados if r['captura_exitosa'])
    capturas_omitidas = sum(1 for r in resultados if not r['captura_exitosa'] and r['cantidad'] == 0)
    errores = sum(1 for r in resultados if r['error'] is not None)

    print()
    print(f"  Total de personas procesadas:     {total}")
    print(f"  Con resultados (> 0):              {con_resultados}")
    print(f"  Sin resultados (= 0):              {sin_resultados}")
    print()
    print(f"  Screenshots capturados:            {capturas_exitosas}")
    print(f"  Screenshots omitidos (cantidad=0): {capturas_omitidas}")
    print(f"  Errores al capturar:               {errores}")
    print()

    # Validar criterios de aceptación
    print("=" * 80)
    print("VALIDACIÓN DE CRITERIOS DE ACEPTACIÓN")
    print("=" * 80)
    print()

    # Criterio 1: Capturar cuando hay resultados
    criterio_1 = all(
        r['captura_exitosa'] or r['error'] is not None
        for r in resultados if r['cantidad'] > 0
    )
    print(f"  [{'✓' if criterio_1 else '✗'}] Capturar screenshot cuando cantidad > 0")

    # Criterio 2: NO capturar cuando no hay resultados
    criterio_2 = all(
        not r['captura_exitosa']
        for r in resultados if r['cantidad'] == 0
    )
    print(f"  [{'✓' if criterio_2 else '✗'}] NO capturar screenshot cuando cantidad = 0")

    # Criterio 3: Formato del nombre correcto
    criterio_3 = all(
        r['formato_correcto']
        for r in resultados if r['captura_exitosa']
    )
    print(f"  [{'✓' if criterio_3 else '✗'}] Formato de nombre correcto (YYYYMMDD_idPersona.png)")

    # Criterio 4: Directorio existe
    criterio_4 = os.path.exists("capturas")
    print(f"  [{'✓' if criterio_4 else '✗'}] Directorio 'capturas/' existe")

    # Criterio 5: Continuar después de error (si hubo errores)
    if errores > 0:
        criterio_5 = True  # Si llegamos aquí, es que continuó
        print(f"  [{'✓' if criterio_5 else '✗'}] Continuar proceso después de error")

    print()
    print("=" * 80)

    # Resultado final
    todos_ok = criterio_1 and criterio_2 and criterio_3 and criterio_4

    if todos_ok:
        print("  ✓✓✓ TODOS LOS CRITERIOS DE ACEPTACIÓN PASARON ✓✓✓")
    else:
        print("  ✗✗✗ ALGUNOS CRITERIOS NO PASARON ✗✗✗")

    print("=" * 80)
    print()

    return todos_ok


# ========================================================================
# FUNCIÓN PRINCIPAL DEL TEST
# ========================================================================

def main():
    """Función principal del test."""

    mostrar_encabezado()

    # ===== PASO 1: Conectar a la base de datos =====
    print("=" * 80)
    print("PASO 1: CONEXIÓN A BASE DE DATOS")
    print("=" * 80)
    print()
    print("  Conectando a la base de datos...")

    connection = conectar_base_datos()
    if not connection:
        print("  ✗ No se pudo continuar sin conexión a la base de datos")
        return False

    print("  ✓ Conexión exitosa")
    print()

    # ===== PASO 2: Obtener personas con información completa =====
    print("=" * 80)
    print("PASO 2: OBTENER PERSONAS CON INFORMACIÓN COMPLETA")
    print("=" * 80)
    print()
    print("  Consultando base de datos...")

    try:
        personas = obtener_personas_validas(connection)
        print(f"  ✓ Se encontraron {len(personas)} personas con información completa")

        # Mostrar listado
        mostrar_listado_personas(personas)

        if not personas:
            print()
            print("  ⚠️  No hay personas para procesar. Finalizando test.")
            connection.close()
            return False

    except Exception as e:
        print(f"  ✗ Error al obtener personas: {e}")
        connection.close()
        return False
    finally:
        # Cerrar conexión a la BD (ya no la necesitamos)
        connection.close()
        print()
        print("  ℹ️  Conexión a BD cerrada")

    # ===== PASO 3: Verificar directorio de capturas =====
    verificar_directorio_capturas()

    # ===== PASO 4: Configurar navegador =====
    print("=" * 80)
    print("PASO 3: CONFIGURACIÓN DEL NAVEGADOR")
    print("=" * 80)
    print()
    print("  Configurando navegador Chrome...")

    try:
        # Usar headless=False para ver el navegador en acción
        # Cambiar a True si quieres ejecución sin interfaz gráfica
        navegador = configurar_navegador(headless=False)
        print("  ✓ Navegador configurado correctamente")
    except Exception as e:
        print(f"  ✗ Error al configurar navegador: {e}")
        return False

    # ===== PASO 5: Crear instancias de las clases =====
    try:
        print()
        print("  Inicializando BuscadorOfac...")
        buscador = BuscadorOfac(navegador)
        print("  ✓ BuscadorOfac inicializado")

        print()
        print("  Inicializando CapturaPantalla...")
        captura = CapturaPantalla(navegador)
        print("  ✓ CapturaPantalla inicializado")
    except Exception as e:
        print(f"  ✗ Error al inicializar componentes: {e}")
        navegador.quit()
        return False

    # ===== PASO 6: Navegar a OFAC =====
    print()
    print("  Navegando al sitio OFAC...")
    if not buscador.navegar_a_ofac():
        print("  ✗ Error al navegar a OFAC")
        navegador.quit()
        return False
    print("  ✓ Navegación exitosa")

    # Establecer zoom al 60% para capturas completas
    print()
    print("  Configurando zoom del navegador...")
    establecer_zoom_navegador(navegador, zoom=60)
    print()

    # ===== PASO 7: Procesar cada persona =====
    print()
    print("=" * 80)
    print("PASO 4: BÚSQUEDA EN OFAC Y CAPTURA DE SCREENSHOTS")
    print("=" * 80)

    resultados = []
    total_personas = len(personas)

    for idx, persona in enumerate(personas, 1):
        resultado = {
            'idPersona': persona['idPersona'],
            'nombrePersona': persona['nombrePersona'],
            'cantidad': 0,
            'captura_exitosa': False,
            'ruta_captura': None,
            'formato_correcto': False,
            'error': None
        }

        try:
            # Mostrar información de la persona
            mostrar_persona(persona, idx, total_personas)

            # Realizar búsqueda en OFAC
            print(f"  [BÚSQUEDA] Buscando en OFAC...")
            resultado_busqueda = buscador.buscar_persona(
                nombre=persona['nombrePersona'],
                direccion=persona['direccion'],
                pais=persona['pais']
            )

            if not resultado_busqueda.exito:
                print(f"  ✗ Error en la búsqueda: {resultado_busqueda.mensaje_error}")
                resultado['error'] = resultado_busqueda.mensaje_error
                resultados.append(resultado)
                continue

            cantidad = resultado_busqueda.cantidad_resultados
            resultado['cantidad'] = cantidad

            # Mostrar resultado de la búsqueda
            mostrar_resultado_busqueda(cantidad)

            # Decisión de captura según HU-08
            if cantidad > 0:
                # DEBE capturar screenshot
                print()
                print(f"  [CAPTURA] Capturando screenshot...")

                # Asegurar zoom al 60% antes de capturar
                establecer_zoom_navegador(navegador, zoom=60)

                try:
                    ruta_captura = captura.capturar(id_persona=persona['idPersona'])

                    if ruta_captura and os.path.exists(ruta_captura):
                        resultado['captura_exitosa'] = True
                        resultado['ruta_captura'] = ruta_captura

                        # Verificar formato del nombre
                        fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
                        nombre_esperado = FORMATO_NOMBRE_CAPTURA.format(
                            fecha=fecha_actual,
                            id_persona=persona['idPersona']
                        )
                        resultado['formato_correcto'] = (
                            os.path.basename(ruta_captura) == nombre_esperado
                        )

                        mostrar_captura_exitosa(ruta_captura, persona['idPersona'])
                    else:
                        mostrar_error_captura("La captura retornó None o el archivo no existe")
                        resultado['error'] = "Captura falló"

                except Exception as e:
                    mostrar_error_captura(str(e))
                    resultado['error'] = str(e)
                    # IMPORTANTE: Continuar con el siguiente registro
            else:
                # NO debe capturar screenshot
                mostrar_sin_captura("Cantidad de resultados = 0")
                resultado['captura_exitosa'] = False

            # Pequeña pausa entre búsquedas
            time.sleep(1)

        except Exception as e:
            print(f"  ✗ Error al procesar persona: {e}")
            resultado['error'] = str(e)

        resultados.append(resultado)

    # ===== PASO 8: Cerrar navegador =====
    print()
    print("=" * 80)
    print("FINALIZANDO")
    print("=" * 80)
    print()
    print("  Cerrando navegador...")
    navegador.quit()
    print("  ✓ Navegador cerrado")

    # ===== PASO 9: Mostrar resumen final =====
    exito = mostrar_resumen_final(resultados)

    return exito


# ========================================================================
# PUNTO DE ENTRADA
# ========================================================================

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("  ⚠️  Test interrumpido por el usuario")
        print("=" * 80)
        print()
        sys.exit(1)
    except Exception as e:
        print()
        print()
        print("=" * 80)
        print(f"  ✗✗✗ ERROR FATAL: {e}")
        print("=" * 80)
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
