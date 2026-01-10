"""
Prueba simple de navegacion al sitio web de OFAC.
Este script abre el navegador, accede a OFAC y verifica los elementos del formulario.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# URL de OFAC
OFAC_URL = "https://sanctionssearch.ofac.treas.gov/"


def test_ofac_website():
    """
    Prueba completa de navegacion y verificacion del sitio OFAC.
    """
    driver = None

    try:
        print("=" * 80)
        print("PRUEBA: Navegacion y verificacion del sitio web de OFAC")
        print("=" * 80)
        print()

        # Configurar opciones del navegador Chrome
        print("[1/6] Configurando navegador Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        print("[OK] Opciones configuradas")
        print()

        # Inicializar el driver
        print("[2/6] Iniciando driver de Chrome...")
        driver = webdriver.Chrome(options=options)
        print("[OK] Driver iniciado")
        print()

        # Navegar a OFAC
        print(f"[3/6] Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)
        print("[OK] Pagina cargada")
        print()

        # Esperar a que cargue el formulario
        print("[4/6] Esperando carga del formulario...")
        wait = WebDriverWait(driver, 15)
        name_field = wait.until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtLastName"))
        )
        print("[OK] Formulario detectado")
        print()

        # Verificar informacion de la pagina
        print("[5/6] Verificando informacion de la pagina...")
        print(f"  Titulo: {driver.title}")
        print(f"  URL: {driver.current_url}")
        print()

        # Verificar elementos del formulario
        print("[6/6] Verificando elementos del formulario...")
        print("-" * 80)

        form_elements = {
            "Campo Name": "ctl00_MainContent_txtLastName",
            "Campo Address": "ctl00_MainContent_txtAddress",
            "Campo City": "ctl00_MainContent_txtCity",
            "Campo Country (dropdown)": "ctl00_MainContent_ddlCountry",
            "Boton Search": "ctl00_MainContent_btnSearch",
            "Boton Reset": "ctl00_MainContent_btnReset"
        }

        elementos_encontrados = 0
        for element_name, element_id in form_elements.items():
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"  [OK] {element_name}")
                elementos_encontrados += 1
            except Exception as e:
                print(f"  [X] {element_name} - No encontrado")

        print()
        print("=" * 80)
        print(f"RESULTADO: {elementos_encontrados}/{len(form_elements)} elementos encontrados")

        if elementos_encontrados == len(form_elements):
            print("STATUS: PRUEBA EXITOSA - Todos los elementos detectados")
        else:
            print("STATUS: PRUEBA PARCIAL - Algunos elementos no detectados")

        print("=" * 80)
        print()
        print("El navegador se mantendra abierto por 5 segundos...")
        time.sleep(5)

        return elementos_encontrados == len(form_elements)

    except TimeoutException:
        print()
        print("[ERROR] Timeout: La pagina tardo demasiado en cargar")
        return False

    except Exception as e:
        print()
        print(f"[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            print()
            print("Cerrando navegador...")
            driver.quit()
            print("[OK] Navegador cerrado")
            print()


if __name__ == "__main__":
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "TEST DE NAVEGACION A OFAC" + " " * 34 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()

    resultado = test_ofac_website()

    print()
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Resultado: {'EXITOSO' if resultado else 'FALLIDO'}")
    print("=" * 80)
    print()
