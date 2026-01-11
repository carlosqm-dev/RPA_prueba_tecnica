"""
Prueba HU-04: Clasificacion e Insercion Masiva de Registros No Consultables
Este test:
1. Clasifica las personas en dos grupos:
   - No cruza con maestra
   - Informacion incompleta
2. Muestra los datos por consola
3. Inserta masivamente en la base de datos usando executemany
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from src.base_datos.repositorio_resultados import RepositorioResultados, Resultado
from src.config.constantes import ESTADO_INFORMACION_INCOMPLETA, ESTADO_NO_CRUZA_MAESTRA


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


def obtener_personas_clasificadas(connection):
    """
    Obtiene y clasifica las personas en dos grupos:
    1. No cruza con maestra (no tiene registro en MaestraDetallePersonas)
    2. Informacion incompleta (tiene registro pero falta direccion o pais)

    Returns:
        tuple: (no_cruzan_maestra, informacion_incompleta, validas)
    """
    query = """
    SELECT
        p."idPersona",
        p."nombrePersona",
        m.direccion,
        m.pais,
        CASE
            WHEN m."idPersona" IS NULL THEN 'NO_CRUZA'
            WHEN m.direccion IS NULL OR m.direccion = 'None' OR m.pais IS NULL OR m.pais = 'None' THEN 'INCOMPLETO'
            ELSE 'VALIDO'
        END as clasificacion
    FROM "Personas" p
    LEFT JOIN "MaestraDetallePersonas" m ON p."idPersona" = m."idPersona"
    WHERE p."aConsultar" = 'Si'
    ORDER BY clasificacion, p."idPersona"
    """

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()

        no_cruzan_maestra = []
        informacion_incompleta = []
        validas = []

        for row in resultados:
            registro = {
                'idPersona': row[0],
                'nombrePersona': row[1],
                'direccion': row[2],
                'pais': row[3]
            }

            if row[4] == 'NO_CRUZA':
                no_cruzan_maestra.append(registro)
            elif row[4] == 'INCOMPLETO':
                informacion_incompleta.append(registro)
            else:
                validas.append(registro)

        return no_cruzan_maestra, informacion_incompleta, validas

    except Exception as e:
        print(f"[ERROR] Error al consultar la base de datos: {e}")
        return [], [], []


def convertir_a_resultados(registros, estado_transaccion):
    """
    Convierte lista de registros a objetos Resultado.

    Args:
        registros: Lista de diccionarios con datos de personas
        estado_transaccion: Estado a asignar

    Returns:
        Lista de objetos Resultado
    """
    resultados = []
    for reg in registros:
        resultado = Resultado(
            id_persona=reg['idPersona'],
            nombre_persona=reg['nombrePersona'],
            pais=reg['pais'] if reg['pais'] else "",
            cantidad_resultados=0,
            estado_transaccion=estado_transaccion
        )
        resultados.append(resultado)
    return resultados


def mostrar_grupo(titulo, registros, mostrar_detalles=True):
    """Muestra un grupo de registros por consola."""
    print()
    print("=" * 80)
    print(f"{titulo}")
    print("=" * 80)
    print(f"Total de registros: {len(registros)}")
    print()

    if not registros:
        print("  [No hay registros en este grupo]")
        return

    if mostrar_detalles:
        for idx, reg in enumerate(registros, 1):
            print(f"{idx}. ID: {reg['idPersona']}")
            print(f"   Nombre: {reg['nombrePersona']}")
            print(f"   Direccion: {reg['direccion'] if reg['direccion'] else '[VACIO]'}")
            print(f"   Pais: {reg['pais'] if reg['pais'] else '[VACIO]'}")
            print()


def insertar_masivamente(no_cruzan, incompletos):
    """
    Inserta masivamente los registros no consultables en la BD.

    Args:
        no_cruzan: Lista de personas que no cruzan con maestra
        incompletos: Lista de personas con informacion incompleta

    Returns:
        tuple: (cantidad_no_cruzan_insertadas, cantidad_incompletos_insertadas)
    """
    print()
    print("=" * 80)
    print("INSERCION MASIVA A BASE DE DATOS")
    print("=" * 80)
    print()

    repo_resultados = RepositorioResultados()

    # Insertar lote de "No cruza con maestra"
    cant_no_cruzan = 0
    if no_cruzan:
        print(f"[1/2] Insertando {len(no_cruzan)} registros 'No cruza con maestra'...")
        resultados_no_cruzan = convertir_a_resultados(no_cruzan, ESTADO_NO_CRUZA_MAESTRA)
        cant_no_cruzan = repo_resultados.insertar_lote(resultados_no_cruzan)
        print(f"[OK] {cant_no_cruzan} registros insertados con estado '{ESTADO_NO_CRUZA_MAESTRA}'")
    else:
        print("[1/2] No hay registros 'No cruza con maestra' para insertar")

    print()

    # Insertar lote de "Informacion incompleta"
    cant_incompletos = 0
    if incompletos:
        print(f"[2/2] Insertando {len(incompletos)} registros 'Informacion incompleta'...")
        resultados_incompletos = convertir_a_resultados(incompletos, ESTADO_INFORMACION_INCOMPLETA)
        cant_incompletos = repo_resultados.insertar_lote(resultados_incompletos)
        print(f"[OK] {cant_incompletos} registros insertados con estado '{ESTADO_INFORMACION_INCOMPLETA}'")
    else:
        print("[2/2] No hay registros 'Informacion incompleta' para insertar")

    print()
    print("=" * 80)
    print(f"TOTAL INSERTADO: {cant_no_cruzan + cant_incompletos} registros")
    print("=" * 80)

    return cant_no_cruzan, cant_incompletos


def main():
    """Funcion principal del test."""
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 10 + "TEST HU-04: CLASIFICACION E INSERCION MASIVA" + " " * 23 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    print()

    print("Este test:")
    print("  1. Clasifica las personas en grupos")
    print("  2. Muestra la clasificacion por consola")
    print("  3. Inserta masivamente en la base de datos")
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
        # Obtener personas clasificadas
        print("[PASO 2] Obteniendo y clasificando personas...")
        no_cruzan, incompletos, validas = obtener_personas_clasificadas(connection)
        print("[OK] Clasificacion completada")

        # Mostrar resultados
        print()
        print("=" * 80)
        print("RESULTADOS DE LA CLASIFICACION")
        print("=" * 80)

        mostrar_grupo("GRUPO 1: NO CRUZA CON MAESTRA", no_cruzan, mostrar_detalles=True)
        mostrar_grupo("GRUPO 2: INFORMACION INCOMPLETA", incompletos, mostrar_detalles=True)
        mostrar_grupo("GRUPO 3: VALIDAS (Para consultar en OFAC)", validas, mostrar_detalles=False)

        # Resumen general
        print()
        print("=" * 80)
        print("RESUMEN GENERAL")
        print("=" * 80)
        total = len(no_cruzan) + len(incompletos) + len(validas)
        print(f"  Total personas con aConsultar = 'Si': {total}")
        print()
        print(f"  No cruza con maestra:      {len(no_cruzan):>3} ({len(no_cruzan)/total*100:.1f}%)")
        print(f"  Informacion incompleta:    {len(incompletos):>3} ({len(incompletos)/total*100:.1f}%)")
        print(f"  Validas para OFAC:         {len(validas):>3} ({len(validas)/total*100:.1f}%)")
        print()
        print(f"  Registros NO consultables: {len(no_cruzan) + len(incompletos):>3} (insercion masiva)")
        print(f"  Registros consultables:    {len(validas):>3} (busqueda en OFAC)")
        print("=" * 80)

        # Insercion masiva
        print()
        print("[PASO 3] Insertando registros masivamente en BD...")
        cant_no_cruzan, cant_incompletos = insertar_masivamente(no_cruzan, incompletos)

        # Resultado final
        print()
        print("=" * 80)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"  Total registros insertados: {cant_no_cruzan + cant_incompletos}")
        print(f"    - No cruza con maestra: {cant_no_cruzan}")
        print(f"    - Informacion incompleta: {cant_incompletos}")
        print("=" * 80)
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
