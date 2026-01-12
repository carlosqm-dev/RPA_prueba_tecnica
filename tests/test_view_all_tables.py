"""
Test para visualizar toda la información de las tablas de la base de datos.
Este test se conecta a la base de datos y muestra por consola todos los registros
de cada tabla del proyecto.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from psycopg2.extras import RealDictCursor


# Configuracion de la base de datos
DB_CONFIG = {
    'host': 'rpa-prevalentware.c3rkad1ay1ao.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'database': 'prueba-tecnica',
    'user': 'user9145',
    'password': 'pruebauser91452023'
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
        return connection
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None


def mostrar_tabla_personas(connection):
    """Consulta y muestra todos los registros de la tabla Personas."""
    print()
    print("=" * 100)
    print("TABLA: Personas")
    print("=" * 100)

    query = """
    SELECT
        id,
        "idPersona",
        "nombrePersona",
        "aConsultar"
    FROM "Personas"
    ORDER BY id
    """

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        print(f"Total de registros: {len(resultados)}")
        print()

        if not resultados:
            print("  [No hay registros en esta tabla]")
            return

        # Mostrar encabezados
        print(f"{'ID':<5} {'idPersona':<12} {'nombrePersona':<60} {'aConsultar':<12}")
        print("-" * 100)

        # Mostrar datos
        for row in resultados:
            print(
                f"{row['id']:<5} "
                f"{row['idPersona']:<12} "
                f"{row['nombrePersona']:<60} "
                f"{row['aConsultar']:<12}"
            )

        print()

    except Exception as e:
        print(f"[ERROR] Error al consultar tabla Personas: {e}")


def mostrar_tabla_maestra(connection):
    """Consulta y muestra todos los registros de la tabla MaestraDetallePersonas."""
    print()
    print("=" * 100)
    print("TABLA: MaestraDetallePersonas")
    print("=" * 100)

    query = """
    SELECT
        id,
        "idPersona",
        direccion,
        pais
    FROM "MaestraDetallePersonas"
    ORDER BY id
    """

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        print(f"Total de registros: {len(resultados)}")
        print()

        if not resultados:
            print("  [No hay registros en esta tabla]")
            return

        # Mostrar encabezados
        print(f"{'ID':<5} {'idPersona':<12} {'direccion':<40} {'pais':<30}")
        print("-" * 100)

        # Mostrar datos
        for row in resultados:
            direccion = str(row['direccion'])[:38] if row['direccion'] else '[VACIO]'
            pais = str(row['pais'])[:28] if row['pais'] else '[VACIO]'

            print(
                f"{row['id']:<5} "
                f"{row['idPersona']:<12} "
                f"{direccion:<40} "
                f"{pais:<30}"
            )

        print()

    except Exception as e:
        print(f"[ERROR] Error al consultar tabla MaestraDetallePersonas: {e}")


def mostrar_tabla_resultados(connection):
    """Consulta y muestra todos los registros de la tabla Resultadosuser9145."""
    print()
    print("=" * 100)
    print("TABLA: Resultadosuser9145")
    print("=" * 100)

    query = """
    SELECT
        id,
        "idPersona",
        "nombrePersona",
        pais,
        "cantidadDeResultados",
        "estadoTransaccion"
    FROM "Resultadosuser9145"
    ORDER BY id
    """

    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        print(f"Total de registros: {len(resultados)}")
        print()

        if not resultados:
            print("  [No hay registros en esta tabla]")
            return

        # Mostrar encabezados
        print(f"{'ID':<5} {'idPersona':<12} {'nombrePersona':<30} {'pais':<15} {'cantResultados':<15} {'estadoTransaccion':<25}")
        print("-" * 120)

        # Mostrar datos
        for row in resultados:
            nombre = str(row['nombrePersona'])[:28] if row['nombrePersona'] else '[VACIO]'
            pais = str(row['pais'])[:13] if row['pais'] else '[VACIO]'

            print(
                f"{row['id']:<5} "
                f"{row['idPersona']:<12} "
                f"{nombre:<30} "
                f"{pais:<15} "
                f"{row['cantidadDeResultados']:<15} "
                f"{row['estadoTransaccion']:<25}"
            )

        print()

    except Exception as e:
        print(f"[ERROR] Error al consultar tabla Resultadosuser9145: {e}")


def mostrar_resumen(connection):
    """Muestra un resumen estadístico de todas las tablas."""
    print()
    print("=" * 100)
    print("RESUMEN DE LA BASE DE DATOS")
    print("=" * 100)

    try:
        cursor = connection.cursor()

        # Contar Personas
        cursor.execute('SELECT COUNT(*) FROM "Personas"')
        total_personas = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM "Personas" WHERE "aConsultar" = \'Si\'')
        personas_consultar = cursor.fetchone()[0]

        # Contar MaestraDetallePersonas
        cursor.execute('SELECT COUNT(*) FROM "MaestraDetallePersonas"')
        total_maestra = cursor.fetchone()[0]

        # Contar Resultados
        cursor.execute('SELECT COUNT(*) FROM "Resultadosuser9145"')
        total_resultados = cursor.fetchone()[0]

        # Contar por estado en Resultados
        cursor.execute('''
            SELECT "estadoTransaccion", COUNT(*)
            FROM "Resultadosuser9145"
            GROUP BY "estadoTransaccion"
        ''')
        estados = cursor.fetchall()

        cursor.close()

        print()
        print(f"  Total de Personas:                    {total_personas}")
        print(f"    - Con aConsultar = 'Si':            {personas_consultar}")
        print()
        print(f"  Total en MaestraDetallePersonas:      {total_maestra}")
        print()
        print(f"  Total de Resultados:                  {total_resultados}")

        if estados:
            print()
            print("  Resultados por Estado:")
            for estado in estados:
                print(f"    - {estado[0]}: {estado[1]}")

        print()
        print("=" * 100)

    except Exception as e:
        print(f"[ERROR] Error al generar resumen: {e}")


def main():
    """Funcion principal del test."""
    print()
    print("#" * 100)
    print("#" + " " * 98 + "#")
    print("#" + " " * 25 + "TEST: VISUALIZACION DE TODAS LAS TABLAS" + " " * 34 + "#")
    print("#" + " " * 98 + "#")
    print("#" * 100)
    print()

    print("Este test muestra toda la informacion almacenada en cada tabla de la base de datos.")
    print()

    # Conectar a la base de datos
    print("[PASO 1] Conectando a la base de datos...")
    connection = conectar_base_datos()

    if not connection:
        print("[ERROR] No se pudo continuar sin conexion a la base de datos")
        return False

    print("[OK] Conexion exitosa")
    print()

    try:
        # Mostrar cada tabla
        print("[PASO 2] Consultando tablas...")
        print()

        mostrar_tabla_personas(connection)
        mostrar_tabla_maestra(connection)
        mostrar_tabla_resultados(connection)

        # Mostrar resumen
        print("[PASO 3] Generando resumen...")
        mostrar_resumen(connection)

        print()
        print("=" * 100)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("=" * 100)
        print()

        return True

    except Exception as e:
        print()
        print(f"[ERROR] Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if connection:
            connection.close()
            print("[OK] Conexion cerrada")
            print()


if __name__ == "__main__":
    resultado = main()
    sys.exit(0 if resultado else 1)
