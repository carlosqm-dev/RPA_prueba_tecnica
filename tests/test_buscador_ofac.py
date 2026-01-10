"""
Pruebas para el buscador OFAC.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraping.navegador import crear_navegador, cerrar_navegador
from src.scraping.buscador_ofac import BuscadorOfac


class TestBuscadorOfac(unittest.TestCase):
    """Pruebas para el buscador OFAC."""

    @classmethod
    def setUpClass(cls):
        """Inicializa el navegador antes de las pruebas."""
        cls.navegador = crear_navegador(headless=True)
        cls.buscador = BuscadorOfac(cls.navegador)

    @classmethod
    def tearDownClass(cls):
        """Cierra el navegador después de las pruebas."""
        cerrar_navegador()

    def test_navegar_a_ofac(self):
        """Verifica que se puede navegar al sitio OFAC."""
        resultado = self.buscador.navegar_a_ofac()
        self.assertTrue(resultado)

    def test_buscar_persona_inexistente(self):
        """Verifica búsqueda de persona que no debería existir."""
        self.buscador.navegar_a_ofac()
        resultado = self.buscador.buscar_persona(
            nombre="NombreInexistenteXYZ123",
            pais="United States"
        )
        self.assertTrue(resultado.exito)
        self.assertEqual(resultado.cantidad_resultados, 0)


if __name__ == '__main__':
    unittest.main()
