"""
Prueba de integracion: Base de datos -> OFAC
Extrae un registro valido de la BD y realiza una busqueda en OFAC.
"""

import sys
from pathlib import Path

# Agregar el directorio raiz al path para importar modulos
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


# Configuracion de la base de datos
DB_CONFIG = {
    'host': 'rpa-prevalentware.c3rkad1ay1ao.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'database': 'prueba-tecnica',
    'user': 'user9145',
    'password': 'pruebauser91452023'
}

# URL de OFAC
OFAC_URL = "https://sanctionssearch.ofac.treas.gov/"

# IDs de elementos OFAC
OFAC_IDS = {
    'campo_nombre': 'ctl00_MainContent_txtLastName',
    'campo_direccion': 'ctl00_MainContent_txtAddress',
    'campo_pais': 'ctl00_MainContent_ddlCountry',
    'boton_buscar': 'ctl00_MainContent_btnSearch',
}


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
        print("[OK] Conexion a la base de datos exitosa")
        return connection
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None


def obtener_registro_valido(connection):
    """
    Obtiene un registro valido para procesar:
    - aConsultar = 'Si'
    - Tiene direccion Y pais en la tabla maestra

    Returns:
        dict con idPersona, nombrePersona, direccion, pais o None
    """
    try:
        cursor = connection.cursor()

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
          AND m.pais IS NOT NULL
          AND m.pais != 'None'
        LIMIT 1
        """

        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()

        if result:
            registro = {
                'idPersona': result[0],
                'nombrePersona': result[1],
                'direccion': result[2],
                'pais': result[3]
            }
            print("[OK] Registro valido encontrado:")
            print(f"  ID: {registro['idPersona']}")
            print(f"  Nombre: {registro['nombrePersona']}")
            print(f"  Direccion: {registro['direccion']}")
            print(f"  Pais: {registro['pais']}")
            return registro
        else:
            print("[ERROR] No se encontraron registros validos")
            return None

    except Exception as e:
        print(f"[ERROR] Error al consultar la base de datos: {e}")
        return None


def buscar_en_ofac(registro):
    """
    Realiza la busqueda del registro en OFAC.

    Args:
        registro: dict con datos de la persona

    Returns:
        int: cantidad de resultados encontrados, o None si hay error
    """
    driver = None

    try:
        print()
        print("=" * 80)
        print("INICIANDO BUSQUEDA EN OFAC")
        print("=" * 80)
        print()

        # Configurar navegador
        print("[1/7] Configurando navegador Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)
        print("[OK]")
        print()

        # Navegar a OFAC
        print(f"[2/7] Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)
        print("[OK]")
        print()

        # Esperar que cargue el formulario
        print("[3/7] Esperando carga del formulario...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, OFAC_IDS['campo_nombre'])))
        print("[OK]")
        print()

        # Llenar campo Name
        print("[4/7] Llenando campo Name...")
        campo_nombre = driver.find_element(By.ID, OFAC_IDS['campo_nombre'])
        campo_nombre.clear()
        campo_nombre.send_keys(registro['nombrePersona'])
        print(f"[OK] Ingresado: {registro['nombrePersona']}")
        print()

        # Llenar campo Address
        print("[5/7] Llenando campo Address...")
        campo_direccion = driver.find_element(By.ID, OFAC_IDS['campo_direccion'])
        campo_direccion.clear()
        campo_direccion.send_keys(registro['direccion'])
        print(f"[OK] Ingresado: {registro['direccion']}")
        print()

        # Seleccionar Country
        print("[6/7] Seleccionando Country...")
        dropdown_pais = Select(driver.find_element(By.ID, OFAC_IDS['campo_pais']))
        dropdown_pais.select_by_visible_text(registro['pais'])
        print(f"[OK] Seleccionado: {registro['pais']}")
        print()

        # Hacer clic en Search
        print("[7/7] Haciendo clic en boton Search...")
        boton_buscar = driver.find_element(By.ID, OFAC_IDS['boton_buscar'])
        boton_buscar.click()
        print("[OK] Busqueda enviada")
        print()

        # Esperar y capturar resultados
        print("Esperando resultados...")
        time.sleep(3)

        try:
            # Buscar el elemento que contiene "Found"
            resultados_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Found')]")
            texto_resultados = resultados_element.text
            print(f"[OK] Resultados: {texto_resultados}")

            # Extraer el numero
            import re
            numeros = re.findall(r'(\d+)\s+Found', texto_resultados)
            cantidad = int(numeros[0]) if numeros else 0

            print()
            print("=" * 80)
            print(f"BUSQUEDA COMPLETADA - {cantidad} RESULTADOS ENCONTRADOS")
            print("=" * 80)
            print()

            # Mantener navegador abierto para visualizar
            print("Manteniendo navegador abierto por 10 segundos para visualizar resultados...")
            time.sleep(10)

            return cantidad

        except Exception as e:
            print(f"[ERROR] No se pudo leer los resultados: {e}")
            print("Manteniendo navegador abierto por 10 segundos...")
            time.sleep(10)
            return None

    except Exception as e:
        print()
        print(f"[ERROR] Error durante la busqueda en OFAC: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if driver:
            print()
            print("Cerrando navegador...")
            driver.quit()
            print("[OK] Navegador cerrado")


def main():
    """Funcion principal de la prueba."""
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 15 + "PRUEBA: BASE DE DATOS -> OFAC" + " " * 33 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()

    print("Esta prueba:")
    print("1. Conecta a la base de datos")
    print("2. Extrae un registro valido (con direccion y pais)")
    print("3. Realiza la busqueda en OFAC")
    print("4. Muestra los resultados")
    print()
    print("=" * 80)
    print()

    # Conectar a la base de datos
    print("[PASO 1] Conectando a la base de datos...")
    connection = conectar_base_datos()

    if not connection:
        print()
        print("[ERROR] No se pudo continuar sin conexion a la base de datos")
        return False

    print()

    try:
        # Obtener registro valido
        print("[PASO 2] Obteniendo registro valido de la base de datos...")
        registro = obtener_registro_valido(connection)

        if not registro:
            print()
            print("[ERROR] No se pudo continuar sin un registro valido")
            return False

        print()

        # Buscar en OFAC
        print("[PASO 3] Realizando busqueda en OFAC...")
        cantidad_resultados = buscar_en_ofac(registro)

        if cantidad_resultados is not None:
            print()
            print("=" * 80)
            print("RESUMEN DE LA PRUEBA")
            print("=" * 80)
            print(f"Persona buscada: {registro['nombrePersona']} (ID: {registro['idPersona']})")
            print(f"Direccion: {registro['direccion']}")
            print(f"Pais: {registro['pais']}")
            print(f"Resultados en OFAC: {cantidad_resultados}")
            print("=" * 80)
            print()
            print("[OK] PRUEBA EXITOSA")
            return True
        else:
            print()
            print("[ERROR] PRUEBA FALLIDA - No se pudieron obtener resultados")
            return False

    finally:
        if connection:
            connection.close()
            print()
            print("[OK] Conexion a base de datos cerrada")


if __name__ == "__main__":
    resultado = main()
    print()
    sys.exit(0 if resultado else 1)
