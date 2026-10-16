"""BL-33 (Gabriel): RN-15. Remova o @skip ao implementar colheita.services.distancia_km."""
from decimal import Decimal
from types import SimpleNamespace
from unittest import skip

from django.test import SimpleTestCase

from colheita.services import distancia_km

CEILANDIA = SimpleNamespace(latitude=Decimal('-15.819700'), longitude=Decimal('-48.108300'))
BRAZLANDIA = SimpleNamespace(latitude=Decimal('-15.675800'), longitude=Decimal('-48.200300'))
PLANALTINA = SimpleNamespace(latitude=Decimal('-15.621400'), longitude=Decimal('-47.649200'))


@skip('Remova ao implementar o BL-33')
class DistanciaTest(SimpleTestCase):
    def test_mesma_localidade_e_zero(self):
        self.assertEqual(distancia_km(CEILANDIA, CEILANDIA), 0)

    def test_distancias_em_linha_reta(self):
        self.assertAlmostEqual(distancia_km(CEILANDIA, BRAZLANDIA), 18.8, delta=0.1)
        self.assertAlmostEqual(distancia_km(CEILANDIA, PLANALTINA), 53.9, delta=0.1)

    def test_e_simetrica(self):
        self.assertEqual(distancia_km(CEILANDIA, PLANALTINA), distancia_km(PLANALTINA, CEILANDIA))
