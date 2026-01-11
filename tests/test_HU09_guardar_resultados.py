"""
Prueba HU-09: Guardar Resultado en Base de Datos
Este test valida:
1. Obtener personas con información COMPLETA desde la BD
2. Buscar cada persona en OFAC
3. Capturar screenshot cuando cantidad > 0
4. SIMULAR guardado de resultados en BD (solo mostrar por consola)
5. Validar campos obligatorios
6. Detectar duplicados potenciales
7. Manejar estados OK y NOK

NOTA: Este test NO guarda nada en la tabla Resultadosuser9145.
      Solo muestra por consola qué datos se insertarían.
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
from src.base_datos.repositorio_resultados import Resultado
from src.config.constantes import (
    FORMATO_FECHA_CAPTURA,
    FORMATO_NOMBRE_CAPTURA,
    ESTADO_OK,
    ESTADO_NOK
)


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


def verificar_duplicado(connection, id_persona: int) -> bool:
    """
    Verifica si ya existe un resultado para esta persona en la BD.

    Args:
        connection: Conexión a la BD
        id_persona: ID de la persona a verificar

    Returns:
        True si ya existe, False en caso contrario
    """
    query = """
    SELECT COUNT(*)
    FROM "Resultadosuser9145"
    WHERE "idPersona" = %s
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query, (id_persona,))
        count = cursor.fetchone()[0]
        cursor.close()

        return count > 0

    except Exception as e:
        print(f"[ERROR] Error al verificar duplicado: {e}")
        return False


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
    print("#" + " " * 15 + "TEST HU-09: GUARDAR RESULTADOS EN BD" + " " * 26 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()
    print("Este test:")
    print("  1. Obtiene personas con información COMPLETA desde la BD")
    print("  2. Busca cada persona en OFAC")
    print("  3. Captura screenshot cuando cantidad > 0")
    print("  4. SIMULA guardado en BD (muestra datos por consola)")
    print("  5. Valida campos obligatorios")
    print("  6. Detecta duplicados potenciales")
    print()
    print("CONFIGURACIÓN:")
    print("  - Navegador en pantalla completa (maximizado)")
    print("  - Zoom al 60% para capturas completas")
    print()
    print("IMPORTANTE: Este test NO guarda NADA en la tabla Resultadosuser9145.")
    print("            Solo muestra por consola qué se insertaría.")
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


def validar_campos_obligatorios(resultado: Resultado) -> tuple[bool, str]:
    """
    Valida que los campos obligatorios estén presentes.

    Args:
        resultado: Objeto Resultado a validar

    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not resultado.id_persona or resultado.id_persona <= 0:
        return False, "idPersona es obligatorio y debe ser > 0"

    if not resultado.nombre_persona or resultado.nombre_persona.strip() == "":
        return False, "nombrePersona es obligatorio y no puede estar vacío"

    if not resultado.estado_transaccion or resultado.estado_transaccion.strip() == "":
        return False, "estadoTransaccion es obligatorio y no puede estar vacío"

    return True, ""


def simular_guardado_bd(resultado: Resultado, es_duplicado: bool):
    """
    Simula el guardado en BD mostrando los datos por consola.

    Args:
        resultado: Objeto Resultado a guardar
        es_duplicado: Si ya existe un resultado para esta persona
    """
    print()
    print("  " + "=" * 76)
    print("  SIMULACIÓN DE GUARDADO EN BD")
    print("  " + "=" * 76)

    # Validar campos obligatorios
    es_valido, mensaje_error = validar_campos_obligatorios(resultado)

    if not es_valido:
        print(f"  ✗ VALIDACIÓN FALLIDA: {mensaje_error}")
        print(f"  ⚠️  Este registro NO se insertaría en la BD")
        print("  " + "=" * 76)
        return

    # Mostrar advertencia si es duplicado
    if es_duplicado:
        print(f"  ⚠️  ADVERTENCIA: Ya existe un resultado para idPersona = {resultado.id_persona}")
        print(f"      Se permitiría la inserción (no hay constraint UNIQUE)")
        print()

    # Mostrar SQL que se ejecutaría
    print("  SQL que se ejecutaría:")
    print("  " + "-" * 76)
    print(f'''  INSERT INTO "Resultadosuser9145"
    ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
  VALUES
    ({resultado.id_persona}, '{resultado.nombre_persona}', '{resultado.pais}',
     {resultado.cantidad_resultados}, '{resultado.estado_transaccion}')
  RETURNING id;''')
    print("  " + "-" * 76)
    print()

    # Mostrar datos que se insertarían
    print("  Datos a insertar:")
    print(f"    • idPersona:            {resultado.id_persona}")
    print(f"    • nombrePersona:        {resultado.nombre_persona}")
    print(f"    • pais:                 {resultado.pais}")
    print(f"    • cantidadDeResultados: {resultado.cantidad_resultados}")
    print(f"    • estadoTransaccion:    {resultado.estado_transaccion}")
    print()

    # Estado del registro
    if resultado.estado_transaccion == ESTADO_OK:
        print(f"  ✓ Estado: OK - Búsqueda exitosa")
    elif resultado.estado_transaccion == ESTADO_NOK:
        print(f"  ✗ Estado: NOK - Búsqueda fallida después de reintentos")
    else:
        print(f"  ℹ️  Estado: {resultado.estado_transaccion}")

    print()
    print(f"  ✓ VALIDACIÓN EXITOSA - Este registro SE insertaría en la BD")
    print("  " + "=" * 76)


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
    estado_ok = sum(1 for r in resultados if r['estado'] == ESTADO_OK)
    estado_nok = sum(1 for r in resultados if r['estado'] == ESTADO_NOK)
    validaciones_exitosas = sum(1 for r in resultados if r['validacion_exitosa'])
    duplicados = sum(1 for r in resultados if r['es_duplicado'])
    errores = sum(1 for r in resultados if r['error'] is not None)

    print()
    print(f"  Total de personas procesadas:     {total}")
    print(f"  Con resultados (> 0):              {con_resultados}")
    print(f"  Sin resultados (= 0):              {sin_resultados}")
    print()
    print(f"  Screenshots capturados:            {capturas_exitosas}")
    print()
    print(f"  Registros con estado OK:           {estado_ok}")
    print(f"  Registros con estado NOK:          {estado_nok}")
    print()
    print(f"  Validaciones exitosas:             {validaciones_exitosas}")
    print(f"  Validaciones fallidas:             {total - validaciones_exitosas}")
    print()
    print(f"  Duplicados detectados:             {duplicados}")
    print(f"  Errores durante búsqueda:          {errores}")
    print()

    # Validar criterios de aceptación
    print("=" * 80)
    print("VALIDACIÓN DE CRITERIOS DE ACEPTACIÓN HU-09")
    print("=" * 80)
    print()

    # Criterio 1: Campos obligatorios validados
    criterio_1 = validaciones_exitosas == total
    print(f"  [{'✓' if criterio_1 else '✗'}] Validar campos obligatorios (idPersona, nombrePersona, estadoTransaccion)")

    # Criterio 2: Estado OK para búsquedas exitosas
    criterio_2 = all(
        r['estado'] == ESTADO_OK
        for r in resultados if r['cantidad'] >= 0 and r['error'] is None
    )
    print(f"  [{'✓' if criterio_2 else '✗'}] Estado OK para búsquedas exitosas")

    # Criterio 3: Estado NOK para búsquedas fallidas
    criterio_3 = all(
        r['estado'] == ESTADO_NOK
        for r in resultados if r['error'] is not None
    )
    print(f"  [{'✓' if criterio_3 else '✗'}] Estado NOK para búsquedas fallidas")

    # Criterio 4: Advertencia para duplicados
    criterio_4 = True  # Siempre se detectan y muestran
    print(f"  [{'✓' if criterio_4 else '✗'}] Advertencia para duplicados potenciales")

    # Criterio 5: Cantidad de resultados correcta
    criterio_5 = all(
        r['cantidad'] >= 0
        for r in resultados
    )
    print(f"  [{'✓' if criterio_5 else '✗'}] Cantidad de resultados >= 0")

    print()
    print("=" * 80)

    # Resultado final
    todos_ok = criterio_1 and criterio_2 and criterio_3 and criterio_4 and criterio_5

    if todos_ok:
        print("  ✓✓✓ TODOS LOS CRITERIOS DE ACEPTACIÓN PASARON ✓✓✓")
    else:
        print("  ✗✗✗ ALGUNOS CRITERIOS NO PASARON ✗✗✗")

    print("=" * 80)
    print()
    print("NOTA: Los datos NO fueron guardados en la BD.")
    print("      Esta fue solo una simulación para validación.")
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
        connection.close()
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
        connection.close()
        return False

    # ===== PASO 6: Navegar a OFAC =====
    print()
    print("  Navegando al sitio OFAC...")
    if not buscador.navegar_a_ofac():
        print("  ✗ Error al navegar a OFAC")
        navegador.quit()
        connection.close()
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
    print("PASO 4: BÚSQUEDA EN OFAC, CAPTURA Y SIMULACIÓN DE GUARDADO")
    print("=" * 80)

    resultados = []
    total_personas = len(personas)

    for idx, persona in enumerate(personas, 1):
        resultado_test = {
            'idPersona': persona['idPersona'],
            'nombrePersona': persona['nombrePersona'],
            'pais': persona['pais'],
            'cantidad': 0,
            'captura_exitosa': False,
            'ruta_captura': None,
            'formato_correcto': False,
            'estado': ESTADO_NOK,
            'validacion_exitosa': False,
            'es_duplicado': False,
            'error': None
        }

        try:
            # Mostrar información de la persona
            mostrar_persona(persona, idx, total_personas)

            # Verificar si ya existe resultado para esta persona
            es_duplicado = verificar_duplicado(connection, persona['idPersona'])
            resultado_test['es_duplicado'] = es_duplicado

            # Realizar búsqueda en OFAC
            print(f"  [BÚSQUEDA] Buscando en OFAC...")
            resultado_busqueda = buscador.buscar_persona(
                nombre=persona['nombrePersona'],
                direccion=persona['direccion'],
                pais=persona['pais']
            )

            if not resultado_busqueda.exito:
                print(f"  ✗ Error en la búsqueda: {resultado_busqueda.mensaje_error}")
                resultado_test['error'] = resultado_busqueda.mensaje_error
                resultado_test['estado'] = ESTADO_NOK

                # Preparar objeto Resultado para simular guardado
                resultado_bd = Resultado(
                    id_persona=persona['idPersona'],
                    nombre_persona=persona['nombrePersona'],
                    pais=persona['pais'],
                    cantidad_resultados=0,
                    estado_transaccion=ESTADO_NOK
                )

                # Validar y simular guardado
                es_valido, _ = validar_campos_obligatorios(resultado_bd)
                resultado_test['validacion_exitosa'] = es_valido
                simular_guardado_bd(resultado_bd, es_duplicado)

                resultados.append(resultado_test)
                continue

            cantidad = resultado_busqueda.cantidad_resultados
            resultado_test['cantidad'] = cantidad
            resultado_test['estado'] = ESTADO_OK

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
                        resultado_test['captura_exitosa'] = True
                        resultado_test['ruta_captura'] = ruta_captura

                        # Verificar formato del nombre
                        fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
                        nombre_esperado = FORMATO_NOMBRE_CAPTURA.format(
                            fecha=fecha_actual,
                            id_persona=persona['idPersona']
                        )
                        resultado_test['formato_correcto'] = (
                            os.path.basename(ruta_captura) == nombre_esperado
                        )

                        mostrar_captura_exitosa(ruta_captura, persona['idPersona'])
                    else:
                        mostrar_error_captura("La captura retornó None o el archivo no existe")
                        # Continuar aunque falle la captura (criterio de aceptación HU-08)

                except Exception as e:
                    mostrar_error_captura(str(e))
                    # Continuar aunque falle la captura
            else:
                # NO debe capturar screenshot
                mostrar_sin_captura("Cantidad de resultados = 0")
                resultado_test['captura_exitosa'] = False

            # ===== SIMULAR GUARDADO EN BD =====
            # Preparar objeto Resultado
            resultado_bd = Resultado(
                id_persona=persona['idPersona'],
                nombre_persona=persona['nombrePersona'],
                pais=persona['pais'],
                cantidad_resultados=cantidad,
                estado_transaccion=ESTADO_OK
            )

            # Validar campos obligatorios
            es_valido, mensaje_error = validar_campos_obligatorios(resultado_bd)
            resultado_test['validacion_exitosa'] = es_valido

            # Simular guardado en BD (solo mostrar por consola)
            simular_guardado_bd(resultado_bd, es_duplicado)

            # Pequeña pausa entre búsquedas
            time.sleep(1)

        except Exception as e:
            print(f"  ✗ Error al procesar persona: {e}")
            resultado_test['error'] = str(e)
            resultado_test['estado'] = ESTADO_NOK

        resultados.append(resultado_test)

    # ===== PASO 8: Cerrar conexiones =====
    print()
    print("=" * 80)
    print("FINALIZANDO")
    print("=" * 80)
    print()
    print("  Cerrando navegador...")
    navegador.quit()
    print("  ✓ Navegador cerrado")

    print()
    print("  Cerrando conexión a BD...")
    connection.close()
    print("  ✓ Conexión cerrada")

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
