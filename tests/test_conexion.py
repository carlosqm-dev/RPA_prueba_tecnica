"""
Pruebas de conexión a la base de datos.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_datos.conexion import (
    inicializar_pool,
    obtener_conexion,
    cerrar_conexion,
    cerrar_pool
)


class TestConexionBaseDatos(unittest.TestCase):
    """Pruebas para la conexión a la base de datos."""

    @classmethod
    def setUpClass(cls):
        """Inicializa el pool antes de las pruebas."""
        inicializar_pool(min_conexiones=1, max_conexiones=5)

    @classmethod
    def tearDownClass(cls):
        """Cierra el pool después de las pruebas."""
        cerrar_pool()

    def test_obtener_conexion(self):
        """Verifica que se puede obtener una conexión."""
        conexion = obtener_conexion()
        self.assertIsNotNone(conexion)
        cerrar_conexion(conexion)

    def test_ejecutar_consulta_simple(self):
        """Verifica que se puede ejecutar una consulta simple."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()
            cursor.close()
            self.assertEqual(resultado[0], 1)
        finally:
            cerrar_conexion(conexion)

    def test_consultar_tablas(self):
        """Verifica que las tablas requeridas existen."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tablas = [row[0] for row in cursor.fetchall()]
            cursor.close()

            self.assertIn('Personas', tablas)
            self.assertIn('MaestraDetallePersonas', tablas)

        finally:
            cerrar_conexion(conexion)


if __name__ == '__main__':
    unittest.main()
