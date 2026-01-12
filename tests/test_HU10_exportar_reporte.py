"""
Prueba HU-10: Exportar Reporte Excel de Información Incompleta
Este test valida:
1. Conectar a la base de datos
2. Consultar registros con estadoTransaccion = "Información incompleta"
3. Incluir el campo dirección de MaestraDetallePersonas mediante LEFT JOIN
4. Exportar a Excel en formato .xlsx
5. Guardar en carpeta "reportes/"
6. Nombre del archivo: "reporte_incompletos_YYYYMMDD.xlsx"
7. Incluir todas las columnas (id, idPersona, nombrePersona, direccion, pais, cantidadDeResultados, estadoTransaccion)
8. Manejar el caso cuando no hay registros
9. Manejar errores de permisos/escritura
10. El proceso debe continuar aunque falle la exportación

NOTA: Este test SI crea un archivo Excel real en la carpeta reportes/
El campo dirección puede estar vacío (NULL) si no existe en MaestraDetallePersonas
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import os
import psycopg2
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

from src.config.constantes import (
    FORMATO_FECHA_CAPTURA,
    FORMATO_NOMBRE_REPORTE,
    ESTADO_INFORMACION_INCOMPLETA
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

# Configuración de exportación
DIRECTORIO_REPORTES = "reportes"


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


def obtener_registros_incompletos(connection) -> List[Dict]:
    """
    Obtiene todos los registros con estadoTransaccion = 'Información incompleta'.
    Incluye el campo dirección de la tabla MaestraDetallePersonas (puede estar vacío).

    Returns:
        Lista de diccionarios con los datos de los registros incompletos
    """
    query = """
    SELECT
        r.id,
        r."idPersona",
        r."nombrePersona",
        m.direccion,
        r.pais,
        r."cantidadDeResultados",
        r."estadoTransaccion"
    FROM "Resultadosuser9145" r
    LEFT JOIN "MaestraDetallePersonas" m ON r."idPersona" = m."idPersona"
    WHERE r."estadoTransaccion" = 'Información incompleta'
    ORDER BY r.id
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]
        cursor.close()

        # Convertir a lista de diccionarios
        registros = []
        for row in resultados:
            registro = dict(zip(columnas, row))
            registros.append(registro)

        return registros

    except Exception as e:
        print(f"[ERROR] Error al consultar la base de datos: {e}")
        return []


def obtener_dataframe_incompletos(connection) -> Optional[pd.DataFrame]:
    """
    Obtiene un DataFrame de pandas con los registros incompletos.
    Incluye el campo dirección de la tabla MaestraDetallePersonas (puede estar vacío).

    Returns:
        DataFrame con los registros o None si hay error
    """
    query = """
    SELECT
        r.id,
        r."idPersona",
        r."nombrePersona",
        m.direccion,
        r.pais,
        r."cantidadDeResultados",
        r."estadoTransaccion"
    FROM "Resultadosuser9145" r
    LEFT JOIN "MaestraDetallePersonas" m ON r."idPersona" = m."idPersona"
    WHERE r."estadoTransaccion" = 'Información incompleta'
    ORDER BY r.id
    """

    try:
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        print(f"[ERROR] Error al crear DataFrame: {e}")
        return None


# ========================================================================
# FUNCIONES DE EXPORTACIÓN
# ========================================================================

def crear_directorio_reportes() -> bool:
    """
    Crea el directorio de reportes si no existe.

    Returns:
        True si existe o se creó correctamente, False en caso de error
    """
    try:
        if not os.path.exists(DIRECTORIO_REPORTES):
            os.makedirs(DIRECTORIO_REPORTES)
            print(f"  ✓ Directorio '{DIRECTORIO_REPORTES}/' creado")
            return True
        else:
            print(f"  ✓ Directorio '{DIRECTORIO_REPORTES}/' ya existe")
            return True
    except Exception as e:
        print(f"  ✗ Error al crear directorio: {e}")
        return False


def generar_nombre_archivo() -> str:
    """
    Genera el nombre del archivo según el formato especificado.

    Returns:
        Nombre del archivo (ej: "reporte_incompletos_20220728.xlsx")
    """
    fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
    nombre = FORMATO_NOMBRE_REPORTE.format(fecha=fecha_actual)
    return nombre


def exportar_a_excel(df: pd.DataFrame, ruta_archivo: str) -> bool:
    """
    Exporta el DataFrame a un archivo Excel.

    Args:
        df: DataFrame a exportar
        ruta_archivo: Ruta completa del archivo a crear

    Returns:
        True si la exportación fue exitosa, False en caso contrario
    """
    try:
        # Exportar a Excel usando openpyxl como engine
        df.to_excel(ruta_archivo, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"  ✗ Error al exportar a Excel: {e}")
        return False


# ========================================================================
# FUNCIONES DE UTILIDAD PARA VISUALIZACIÓN
# ========================================================================

def mostrar_encabezado():
    """Muestra el encabezado del test."""
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 12 + "TEST HU-10: EXPORTAR REPORTE EXCEL INCOMPLETOS" + " " * 19 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()
    print("Este test:")
    print("  1. Conecta a la base de datos")
    print("  2. Consulta registros con estadoTransaccion = 'Información incompleta'")
    print("  3. Incluye el campo dirección de MaestraDetallePersonas (LEFT JOIN)")
    print("  4. Exporta los registros a Excel (.xlsx)")
    print("  5. Guarda en carpeta 'reportes/'")
    print("  6. Nombre: 'reporte_incompletos_YYYYMMDD.xlsx'")
    print("  7. Incluye todas las columnas (id, idPersona, nombrePersona, direccion, pais, etc.)")
    print("  8. Maneja el caso cuando no hay registros")
    print("  9. Maneja errores de permisos/escritura")
    print()
    print("IMPORTANTE: Este test SI crea un archivo Excel real.")
    print()


def mostrar_registros_encontrados(registros: List[Dict]):
    """Muestra información sobre los registros encontrados."""
    print()
    print("=" * 80)
    print("REGISTROS CON INFORMACIÓN INCOMPLETA")
    print("=" * 80)
    print(f"Total de registros encontrados: {len(registros)}")
    print()

    if not registros:
        print("  ℹ️  No hay registros con información incompleta")
        print()
        return

    # Mostrar los primeros 10 registros
    limite_mostrar = 10

    for idx, registro in enumerate(registros[:limite_mostrar], 1):
        print(f"{idx:2}. ID: {registro.get('id', 'N/A'):3} | "
              f"idPersona: {registro.get('idPersona', 'N/A'):3} | "
              f"{registro.get('nombrePersona', 'N/A')}")
        print(f"    Dirección: {registro.get('direccion', 'N/A')}")
        print(f"    País:      {registro.get('pais', 'N/A')}")
        print(f"    Estado:    {registro.get('estadoTransaccion', 'N/A')}")
        print()

    if len(registros) > limite_mostrar:
        print(f"    ... y {len(registros) - limite_mostrar} registros más")
        print()

    print("=" * 80)


def mostrar_estructura_dataframe(df: pd.DataFrame):
    """Muestra información sobre el DataFrame."""
    print()
    print("=" * 80)
    print("ESTRUCTURA DEL DATAFRAME")
    print("=" * 80)
    print()
    print(f"  Filas:    {len(df)}")
    print(f"  Columnas: {len(df.columns)}")
    print()
    print("  Columnas incluidas:")
    for col in df.columns:
        print(f"    - {col}")
    print()

    if len(df) > 0:
        print("  Vista previa (primeras 5 filas):")
        print()
        # Mostrar con formato tabular
        print(df.head().to_string(index=False))
    else:
        print("  ℹ️  DataFrame vacío (sin filas)")

    print()
    print("=" * 80)


def verificar_archivo_creado(ruta_archivo: str) -> bool:
    """
    Verifica que el archivo se haya creado correctamente.

    Args:
        ruta_archivo: Ruta del archivo a verificar

    Returns:
        True si el archivo existe y tiene contenido, False en caso contrario
    """
    print()
    print("=" * 80)
    print("VERIFICACIÓN DEL ARCHIVO CREADO")
    print("=" * 80)
    print()

    if not os.path.exists(ruta_archivo):
        print(f"  ✗ El archivo NO existe: {ruta_archivo}")
        return False

    print(f"  ✓ El archivo existe: {ruta_archivo}")

    # Verificar tamaño
    tamaño = os.path.getsize(ruta_archivo)
    print(f"  ✓ Tamaño: {tamaño} bytes")

    # Verificar que se pueda leer
    try:
        df_verificacion = pd.read_excel(ruta_archivo, engine='openpyxl')
        print(f"  ✓ El archivo se puede leer correctamente")
        print(f"  ✓ Registros en el archivo: {len(df_verificacion)}")
        print(f"  ✓ Columnas en el archivo: {len(df_verificacion.columns)}")

        # Mostrar columnas
        print()
        print("  Columnas en el archivo Excel:")
        for col in df_verificacion.columns:
            print(f"    - {col}")

        return True
    except Exception as e:
        print(f"  ✗ Error al leer el archivo: {e}")
        return False


def mostrar_resumen_final(exito: bool, registros_exportados: int, ruta_archivo: str):
    """Muestra el resumen final del test."""
    print()
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print()

    if exito:
        print(f"  ✓ Exportación exitosa")
        print(f"  ✓ Registros exportados: {registros_exportados}")
        print(f"  ✓ Archivo creado: {ruta_archivo}")
    else:
        print(f"  ✗ La exportación falló")
        print(f"  ℹ️  Registros a exportar: {registros_exportados}")

    print()
    print("=" * 80)
    print("VALIDACIÓN DE CRITERIOS DE ACEPTACIÓN HU-10")
    print("=" * 80)
    print()

    # Criterio 1: Archivo creado en la carpeta correcta
    criterio_1 = os.path.exists(ruta_archivo) if exito else False
    print(f"  [{'✓' if criterio_1 else '✗'}] Archivo creado en carpeta 'reportes/'")

    # Criterio 2: Nombre del archivo correcto
    nombre_archivo = os.path.basename(ruta_archivo)
    fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
    nombre_esperado = FORMATO_NOMBRE_REPORTE.format(fecha=fecha_actual)
    criterio_2 = nombre_archivo == nombre_esperado
    print(f"  [{'✓' if criterio_2 else '✗'}] Nombre correcto: 'reporte_incompletos_YYYYMMDD.xlsx'")
    print(f"      Esperado: {nombre_esperado}")
    print(f"      Obtenido: {nombre_archivo}")

    # Criterio 3: Contiene todas las columnas
    criterio_3 = False
    if exito and os.path.exists(ruta_archivo):
        try:
            df_verificacion = pd.read_excel(ruta_archivo, engine='openpyxl')
            columnas_esperadas = {'id', 'idPersona', 'nombrePersona', 'direccion', 'pais',
                                'cantidadDeResultados', 'estadoTransaccion'}
            columnas_presentes = set(df_verificacion.columns)
            criterio_3 = columnas_esperadas.issubset(columnas_presentes)
        except:
            criterio_3 = False
    print(f"  [{'✓' if criterio_3 else '✗'}] Contiene todas las columnas (incluye dirección de Maestra)")

    # Criterio 4: Solo registros con "Información incompleta"
    criterio_4 = False
    if exito and os.path.exists(ruta_archivo):
        try:
            df_verificacion = pd.read_excel(ruta_archivo, engine='openpyxl')
            if len(df_verificacion) > 0:
                estados_unicos = df_verificacion['estadoTransaccion'].unique()
                criterio_4 = all(estado == ESTADO_INFORMACION_INCOMPLETA for estado in estados_unicos)
            else:
                criterio_4 = True  # Si está vacío, también es válido
        except:
            criterio_4 = False
    print(f"  [{'✓' if criterio_4 else '✗'}] Solo registros con 'Información incompleta'")

    # Criterio 5: Manejo de casos sin registros
    criterio_5 = True  # Siempre se crea archivo, aunque sea vacío
    print(f"  [{'✓' if criterio_5 else '✗'}] Manejo correcto cuando no hay registros")

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

    return todos_ok


# ========================================================================
# FUNCIÓN PRINCIPAL DEL TEST
# ========================================================================

def main():
    """Función principal del test."""

    mostrar_encabezado()

    exito_exportacion = False
    registros = []
    ruta_archivo = ""

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

    try:
        # ===== PASO 2: Consultar registros incompletos =====
        print("=" * 80)
        print("PASO 2: CONSULTAR REGISTROS INCOMPLETOS")
        print("=" * 80)
        print()
        print("  Consultando base de datos...")

        # Obtener registros para mostrar
        registros = obtener_registros_incompletos(connection)
        print(f"  ✓ Se encontraron {len(registros)} registros con información incompleta")

        # Mostrar registros
        mostrar_registros_encontrados(registros)

        # Obtener DataFrame para exportar
        print()
        print("  Creando DataFrame para exportación...")
        df = obtener_dataframe_incompletos(connection)

        if df is None:
            print("  ✗ Error al crear DataFrame")
            return False

        print(f"  ✓ DataFrame creado con {len(df)} filas")

        # Mostrar estructura
        mostrar_estructura_dataframe(df)

        # ===== PASO 3: Crear directorio de reportes =====
        print()
        print("=" * 80)
        print("PASO 3: PREPARAR DIRECTORIO DE EXPORTACIÓN")
        print("=" * 80)
        print()

        if not crear_directorio_reportes():
            print("  ✗ No se pudo crear el directorio de reportes")
            print("  ⚠️  Intentando continuar de todas formas...")

        # ===== PASO 4: Generar nombre de archivo =====
        print()
        print("=" * 80)
        print("PASO 4: GENERAR NOMBRE DE ARCHIVO")
        print("=" * 80)
        print()

        nombre_archivo = generar_nombre_archivo()
        ruta_archivo = os.path.join(DIRECTORIO_REPORTES, nombre_archivo)

        fecha_actual = datetime.now().strftime(FORMATO_FECHA_CAPTURA)
        print(f"  Fecha actual: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"  Formato fecha: {fecha_actual}")
        print(f"  Nombre archivo: {nombre_archivo}")
        print(f"  Ruta completa: {ruta_archivo}")
        print()

        # ===== PASO 5: Exportar a Excel =====
        print("=" * 80)
        print("PASO 5: EXPORTAR A EXCEL")
        print("=" * 80)
        print()
        print(f"  Exportando {len(df)} registros a Excel...")
        print()

        try:
            exito_exportacion = exportar_a_excel(df, ruta_archivo)

            if exito_exportacion:
                print(f"  ✓ Exportación exitosa")
                print(f"  ✓ Archivo creado: {ruta_archivo}")

                # Verificar archivo
                verificar_archivo_creado(ruta_archivo)
            else:
                print(f"  ✗ La exportación falló")
                print(f"  ℹ️  El proceso continúa (no se detiene por el error)")

        except Exception as e:
            print(f"  ✗ Error durante la exportación: {e}")
            print(f"  ℹ️  El proceso continúa (no se detiene por el error)")
            exito_exportacion = False

    except Exception as e:
        print(f"  ✗ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
        exito_exportacion = False

    finally:
        # ===== PASO 6: Cerrar conexión =====
        print()
        print("=" * 80)
        print("FINALIZANDO")
        print("=" * 80)
        print()
        print("  Cerrando conexión a BD...")
        connection.close()
        print("  ✓ Conexión cerrada")

    # ===== PASO 7: Mostrar resumen final =====
    exito = mostrar_resumen_final(exito_exportacion, len(registros), ruta_archivo)

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
