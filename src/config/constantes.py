"""
Constantes del proyecto.
"""

# Nombres de tablas en la base de datos
TABLA_PERSONAS = '"Personas"'
TABLA_MAESTRA = '"MaestraDetallePersonas"'
TABLA_RESULTADOS = '"Resultadosuser9145"'

# Estados de transacción
ESTADO_OK = "OK"
ESTADO_NOK = "NOK"
ESTADO_INFORMACION_INCOMPLETA = "Información incompleta"
ESTADO_NO_CRUZA_MAESTRA = "No cruza con maestra"

# Valores para el campo aConsultar
CONSULTAR_SI = "Si"
CONSULTAR_NO = "No"

# Formatos
FORMATO_FECHA_CAPTURA = "%Y%m%d"
FORMATO_NOMBRE_CAPTURA = "{fecha}_{id_persona}.png"
FORMATO_NOMBRE_REPORTE = "reporte_incompletos_{fecha}.xlsx"

# Selectores CSS/XPath para OFAC
# IDs verificados mediante pruebas en el sitio real
SELECTORES_OFAC = {
    'campo_nombre': '#ctl00_MainContent_txtLastName',  # Campo Name
    'campo_direccion': '#ctl00_MainContent_txtAddress',  # Campo Address
    'campo_ciudad': '#ctl00_MainContent_txtCity',  # Campo City
    'campo_pais': '#ctl00_MainContent_ddlCountry',  # Dropdown Country
    'boton_buscar': '#ctl00_MainContent_btnSearch',  # Boton Search
    'boton_reset': '#ctl00_MainContent_btnReset',  # Boton Reset
    'resultado_conteo': '#ctl00_MainContent_lbResults'  # Texto "X Found"
}

# Configuración de reintentos
MAX_REINTENTOS = 3
TIEMPO_ENTRE_REINTENTOS = 2
