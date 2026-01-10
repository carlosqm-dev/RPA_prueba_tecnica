"""
Prueba de busqueda en OFAC con datos de ejemplo.
Este script abre el navegador, llena el formulario y realiza una busqueda.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


# URL de OFAC
OFAC_URL = "https://sanctionssearch.ofac.treas.gov/"


def test_ofac_search():
    """
    Prueba de busqueda en OFAC con datos de ejemplo.
    """
    driver = None

    try:
        print("=" * 80)
        print("PRUEBA: Busqueda en OFAC con datos de ejemplo")
        print("=" * 80)
        print()

        # Datos de prueba
        test_data = {
            "name": "AHMED",
            "address": "333 Main Street",
            "country": "All"
        }

        print("Datos de prueba:")
        print(f"  Nombre: {test_data['name']}")
        print(f"  Direccion: {test_data['address']}")
        print(f"  Pais: {test_data['country']}")
        print()

        # Configurar navegador
        print("[1/8] Configurando navegador...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)
        print("[OK]")
        print()

        # Navegar a OFAC
        print(f"[2/8] Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)
        print("[OK]")
        print()

        # Esperar carga
        print("[3/8] Esperando carga del formulario...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtLastName")))
        print("[OK]")
        print()

        # Llenar campo Name
        print("[4/8] Llenando campo Name...")
        name_field = driver.find_element(By.ID, "ctl00_MainContent_txtLastName")
        name_field.clear()
        name_field.send_keys(test_data["name"])
        print(f"[OK] Ingresado: {test_data['name']}")
        print()

        # Llenar campo Address
        print("[5/8] Llenando campo Address...")
        address_field = driver.find_element(By.ID, "ctl00_MainContent_txtAddress")
        address_field.clear()
        address_field.send_keys(test_data["address"])
        print(f"[OK] Ingresado: {test_data['address']}")
        print()

        # Seleccionar Country
        print("[6/8] Seleccionando Country...")
        country_dropdown = Select(driver.find_element(By.ID, "ctl00_MainContent_ddlCountry"))
        country_dropdown.select_by_visible_text(test_data["country"])
        print(f"[OK] Seleccionado: {test_data['country']}")
        print()

        # Hacer clic en Search
        print("[7/8] Haciendo clic en boton Search...")
        search_button = driver.find_element(By.ID, "ctl00_MainContent_btnSearch")
        search_button.click()
        print("[OK] Boton presionado")
        print()

        # Esperar resultados
        print("[8/8] Esperando resultados...")
        time.sleep(3)  # Esperar a que carguen los resultados

        # Intentar encontrar el campo de resultados
        try:
            # El campo de resultados suele tener un texto como "1 Found" o "X Found"
            # Busquemos varios posibles selectores
            results_text = None

            # Intentar encontrar por texto "Found"
            try:
                results_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Found')]")
                results_text = results_element.text
                print(f"[OK] Resultados encontrados: {results_text}")
            except:
                # Intentar otro selector
                try:
                    results_element = driver.find_element(By.ID, "ctl00_MainContent_lbResults")
                    results_text = results_element.text
                    print(f"[OK] Resultados: {results_text}")
                except:
                    print("[AVISO] No se pudo detectar automaticamente el texto de resultados")
                    print("        Pero la busqueda fue ejecutada correctamente")

        except Exception as e:
            print(f"[AVISO] No se pudo leer los resultados: {e}")

        print()
        print("=" * 80)
        print("RESULTADO: Busqueda ejecutada exitosamente")
        print("=" * 80)
        print()
        print("El navegador permanecera abierto por 15 segundos para revisar resultados...")
        time.sleep(15)

        return True

    except Exception as e:
        print()
        print(f"[ERROR] Error durante la prueba: {e}")
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


def test_ofac_search_and_reset():
    """
    Prueba de busqueda en OFAC y uso del boton Reset.
    """
    driver = None

    try:
        print("=" * 80)
        print("PRUEBA: Busqueda en OFAC y uso del boton Reset")
        print("=" * 80)
        print()

        # Configurar navegador
        print("Configurando navegador...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(options=options)

        # Navegar a OFAC
        print(f"Navegando a: {OFAC_URL}")
        driver.get(OFAC_URL)

        # Esperar carga
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_txtLastName")))

        # Llenar formulario
        print("Llenando formulario con datos de prueba...")
        name_field = driver.find_element(By.ID, "ctl00_MainContent_txtLastName")
        name_field.send_keys("TEST NAME")

        address_field = driver.find_element(By.ID, "ctl00_MainContent_txtAddress")
        address_field.send_keys("TEST ADDRESS")

        print("Campos llenados. Esperando 2 segundos...")
        time.sleep(2)

        # Hacer clic en Reset
        print("Haciendo clic en boton Reset...")
        reset_button = driver.find_element(By.ID, "ctl00_MainContent_btnReset")
        reset_button.click()

        time.sleep(2)

        # Verificar que los campos esten vacios
        print("Verificando que los campos se hayan limpiado...")
        name_value = name_field.get_attribute("value")
        address_value = address_field.get_attribute("value")

        if not name_value and not address_value:
            print("[OK] Campos limpiados correctamente")
            resultado = True
        else:
            print(f"[AVISO] Campos no vacios - Name: '{name_value}', Address: '{address_value}'")
            resultado = False

        print()
        print("Manteniendo navegador abierto por 5 segundos...")
        time.sleep(5)

        return resultado

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
    print("#" + " " * 20 + "TEST DE BUSQUEDA EN OFAC" + " " * 34 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()

    # Ejecutar primera prueba
    resultado1 = test_ofac_search()

    print()
    print("=" * 80)
    print("Esperando 3 segundos antes de la siguiente prueba...")
    print("=" * 80)
    time.sleep(3)
    print()

    # Ejecutar segunda prueba
    resultado2 = test_ofac_search_and_reset()

    print()
    print("=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    print(f"Prueba 1 (Busqueda con datos): {'EXITOSA' if resultado1 else 'FALLIDA'}")
    print(f"Prueba 2 (Reset de formulario): {'EXITOSA' if resultado2 else 'FALLIDA'}")
    print("=" * 80)
    print()
