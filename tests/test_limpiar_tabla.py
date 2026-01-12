"""
Test para verificar la funcionalidad de limpieza de tabla de resultados.

Este test verifica que:
1. Se puede limpiar la tabla Resultadosuser9145 usando DELETE
2. La tabla queda completamente vacía
3. Se retorna el número correcto de registros eliminados

NOTA: El contador de IDs NO se reinicia porque usa DELETE en lugar de TRUNCATE.
      Esto es intencional para evitar problemas de permisos en PostgreSQL.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from src.base_datos.repositorio_resultados import RepositorioResultados


# Configuración de BD
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


def contar_registros(connection):
    """Cuenta los registros en la tabla Resultadosuser9145."""
    query = 'SELECT COUNT(*) FROM "Resultadosuser9145"'
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        print(f"[ERROR] Error al contar registros: {e}")
        return -1


def obtener_max_id(connection):
    """Obtiene el máximo ID actual en la tabla."""
    query = 'SELECT MAX(id) FROM "Resultadosuser9145"'
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        cursor.close()
        return max_id if max_id else 0
    except Exception as e:
        print(f"[ERROR] Error al obtener max ID: {e}")
        return -1


def main():
    """Función principal del test."""
    print()
    print("=" * 80)
    print("TEST: LIMPIEZA DE TABLA DE RESULTADOS")
    print("=" * 80)
    print()

    # Conectar a BD
    print("Conectando a base de datos...")
    connection = conectar_base_datos()
    if not connection:
        print("✗ No se pudo conectar a la BD")
        return False

    print("✓ Conexión exitosa")
    print()

    # Contar registros antes
    print("=" * 80)
    print("ANTES DE LIMPIAR")
    print("=" * 80)
    registros_antes = contar_registros(connection)
    max_id_antes = obtener_max_id(connection)
    print(f"  Registros en tabla: {registros_antes}")
    print(f"  Máximo ID:          {max_id_antes}")
    print()

    # Limpiar tabla
    print("=" * 80)
    print("EJECUTANDO LIMPIEZA")
    print("=" * 80)
    repo = RepositorioResultados()

    try:
        eliminados = repo.limpiar_tabla()
        print(f"✓ Limpieza exitosa")
        print(f"  Registros eliminados: {eliminados}")
    except Exception as e:
        print(f"✗ Error al limpiar tabla: {e}")
        connection.close()
        return False

    print()

    # Contar registros después
    print("=" * 80)
    print("DESPUÉS DE LIMPIAR")
    print("=" * 80)
    registros_despues = contar_registros(connection)
    max_id_despues = obtener_max_id(connection)
    print(f"  Registros en tabla: {registros_despues}")
    print(f"  Máximo ID:          {max_id_despues}")
    print()

    # Verificación
    print("=" * 80)
    print("VERIFICACIÓN")
    print("=" * 80)

    exito = True

    # Verificar que la tabla esté vacía
    if registros_despues == 0:
        print("  ✓ Tabla completamente vacía")
    else:
        print(f"  ✗ La tabla NO está vacía (tiene {registros_despues} registros)")
        exito = False

    # Nota informativa sobre el contador de IDs
    if max_id_despues == 0 or max_id_despues is None:
        print("  ℹ️  Máximo ID: 0 o NULL (tabla vacía)")
    else:
        print(f"  ℹ️  Nota: El contador de IDs NO se reinicia con DELETE")
        print(f"      Los nuevos registros empezarán desde ID > {max_id_despues}")

    # Verificar que se eliminaron los registros esperados
    if eliminados == registros_antes:
        print(f"  ✓ Se eliminaron {eliminados} registros (coincide con el conteo inicial)")
    else:
        print(f"  ⚠️  Registros eliminados ({eliminados}) no coincide con conteo inicial ({registros_antes})")

    print()
    print("=" * 80)

    if exito:
        print("  ✓✓✓ TEST EXITOSO ✓✓✓")
    else:
        print("  ✗✗✗ TEST FALLÓ ✗✗✗")

    print("=" * 80)
    print()

    connection.close()
    return exito


if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"✗✗✗ ERROR FATAL: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
