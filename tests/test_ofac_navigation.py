"""
Prueba de navegacion al sitio web de OFAC.
Este script abre el navegador y accede a la plataforma de sanciones de OFAC.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


# URL de OFAC
OFAC_URL = "https://sanctionssearch.ofac.treas.gov/"


def test_open_ofac_website():
    """
    Prueba para abrir el sitio web de OFAC y verificar que carga correctamente.
    """
    driver = None

    try:
        print("=" * 80)
        print("PRUEBA: Navegacion al sitio web de OFAC")
        print("=" * 80)
        print()

        # Configurar opciones del navegador Chrome
        print("[1/5] Configurando opciones del navegador Chrome...")
        options = webdriver.ChromeOptions()

        # Opciones recomendadas para automatizacion
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Descomentar la siguiente linea si quieres ejecutar en modo headless (sin ventana)
        # options.add_argument('--headless')

        print("[OK] Opciones configuradas")
        print()

        # Inicializar el driver de Chrome
        print("[2/5] Iniciando driver de Chrome...")
        driver = webdriver.Chrome(options=options)
        print("[OK] Driver iniciado correctamente")
        print()

        # Navegar a la URL de OFAC
        print(f"[3/5] Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)
        print("[OK] Pagina cargada")
        print()

        # Esperar a que la pagina cargue completamente
        print("[4/5] Esperando a que la pagina cargue completamente...")
        wait = WebDriverWait(driver, 15)

        # Esperar a que aparezca el formulario de busqueda
        # Buscamos el campo "Name" que es uno de los elementos principales
        try:
            name_field = wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtLastName"))
            )
            print("[OK] Formulario de busqueda detectado")
        except TimeoutException:
            print("[AVISO] No se pudo detectar el formulario en 15 segundos")
            print("        Intentando verificar si la pagina cargo...")

        print()

        # Obtener informacion de la pagina
        print("[5/5] Verificando informacion de la pagina...")
        print(f"  Titulo de la pagina: {driver.title}")
        print(f"  URL actual: {driver.current_url}")
        print()

        # Intentar identificar elementos clave del formulario
        print("Elementos del formulario detectados:")
        print("-" * 80)

        form_elements = {
            "Campo Name": "ctl00_MainContent_txtLastName",
            "Campo Address": "ctl00_MainContent_txtAddress",
            "Campo City": "ctl00_MainContent_txtCity",
            "Campo Country": "ctl00_MainContent_ddlCountry",
            "Boton Search": "ctl00_MainContent_btnSearch",
            "Boton Reset": "ctl00_MainContent_btnReset"
        }

        for element_name, element_id in form_elements.items():
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"  [OK] {element_name}: Encontrado")
            except Exception:
                print(f"  [X] {element_name}: No encontrado")

        print()
        print("=" * 80)
        print("RESULTADO: Prueba completada exitosamente")
        print("=" * 80)
        print()
        print("El navegador permanecera abierto por 10 segundos para inspeccion...")
        print("Presiona Ctrl+C para cerrar inmediatamente")

        # Mantener el navegador abierto por un tiempo
        time.sleep(10)

        return True

    except WebDriverException as e:
        print()
        print("[ERROR] Error al iniciar el driver de Chrome")
        print(f"Detalle: {e}")
        print()
        print("Posibles soluciones:")
        print("1. Asegurate de tener Chrome instalado")
        print("2. Verifica que ChromeDriver este instalado y actualizado")
        print("3. Ejecuta: pip install --upgrade selenium")
        return False

    except Exception as e:
        print()
        print(f"[ERROR] Error inesperado: {e}")
        return False

    finally:
        # Cerrar el navegador
        if driver:
            print()
            print("Cerrando navegador...")
            driver.quit()
            print("[OK] Navegador cerrado")


def test_inspect_ofac_form():
    """
    Prueba mas detallada que inspecciona el formulario de OFAC
    y muestra toda la estructura HTML relevante.
    """
    driver = None

    try:
        print("=" * 80)
        print("PRUEBA: Inspeccion detallada del formulario OFAC")
        print("=" * 80)
        print()

        # Inicializar driver
        print("Iniciando navegador...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(options=options)

        # Navegar a OFAC
        print(f"Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)

        # Esperar carga
        wait = WebDriverWait(driver, 15)
        time.sleep(3)  # Espera adicional para asegurar carga completa

        print()
        print("=" * 80)
        print("INFORMACION DE LA PAGINA")
        print("=" * 80)
        print(f"Titulo: {driver.title}")
        print(f"URL: {driver.current_url}")
        print()

        # Buscar todos los campos de entrada
        print("=" * 80)
        print("CAMPOS DE ENTRADA (input)")
        print("=" * 80)
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for idx, inp in enumerate(inputs[:10], 1):  # Limitamos a los primeros 10
            input_type = inp.get_attribute("type")
            input_id = inp.get_attribute("id")
            input_name = inp.get_attribute("name")
            input_value = inp.get_attribute("value")
            print(f"{idx}. Type: {input_type}, ID: {input_id}, Name: {input_name}, Value: {input_value}")
        print()

        # Buscar dropdowns
        print("=" * 80)
        print("CAMPOS DESPLEGABLES (select)")
        print("=" * 80)
        selects = driver.find_elements(By.TAG_NAME, "select")
        for idx, sel in enumerate(selects, 1):
            select_id = sel.get_attribute("id")
            select_name = sel.get_attribute("name")
            print(f"{idx}. ID: {select_id}, Name: {select_name}")
        print()

        # Buscar botones
        print("=" * 80)
        print("BOTONES")
        print("=" * 80)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for idx, btn in enumerate(buttons, 1):
            btn_id = btn.get_attribute("id")
            btn_text = btn.text
            btn_type = btn.get_attribute("type")
            print(f"{idx}. ID: {btn_id}, Text: {btn_text}, Type: {btn_type}")

        # Tambien buscar inputs tipo button/submit
        input_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='button'], input[type='submit']")
        for idx, btn in enumerate(input_buttons, len(buttons) + 1):
            btn_id = btn.get_attribute("id")
            btn_value = btn.get_attribute("value")
            print(f"{idx}. ID: {btn_id}, Value: {btn_value}")
        print()

        print("=" * 80)
        print("Inspeccion completada")
        print("=" * 80)
        print()
        print("Manteniendo navegador abierto por 15 segundos...")
        time.sleep(15)

        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            print("Cerrando navegador...")
            driver.quit()


if __name__ == "__main__":
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "TEST DE NAVEGACION A OFAC" + " " * 34 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()

    # Ejecutar primera prueba
    resultado1 = test_open_ofac_website()

    print()
    input("Presiona ENTER para ejecutar la segunda prueba (inspeccion detallada)...")
    print()

    # Ejecutar segunda prueba
    resultado2 = test_inspect_ofac_form()

    print()
    print("=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    print(f"Prueba 1 (Navegacion basica): {'EXITOSA' if resultado1 else 'FALLIDA'}")
    print(f"Prueba 2 (Inspeccion detallada): {'EXITOSA' if resultado2 else 'FALLIDA'}")
    print("=" * 80)
