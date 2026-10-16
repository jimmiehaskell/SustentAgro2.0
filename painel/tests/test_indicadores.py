"""BL-37 (Pedro): RF-29, RN-08 a RN-11, P-01. Remova o @skip ao implementar painel.services.indicadores
(depende de BL-24 a BL-26)."""
from decimal import Decimal
from unittest import skip

from django.test import TestCase

from core.tests.fabricas import criar_oferta, criar_ong


def _valor(indicadores, nome):
    return indicadores[nome] if isinstance(indicadores, dict) else getattr(indicadores, nome)


@skip('Remova ao implementar o BL-37')
class IndicadoresTest(TestCase):
    def setUp(self):
        from colheita.models import Reserva
        ong = criar_ong(familias_por_mes=180)
        criar_ong(familias_por_mes=60)
        criar_ong(situacao='pendente', familias_por_mes=999)  # não conta (RN-10, RN-11)
        venda = criar_oferta(quantidade='100', destino='vender', preco_unitario='2.50')
        doacao = criar_oferta(quantidade='50')
        em_unidades = criar_oferta(quantidade='40', unidade='un')
        Reserva.objects.create(oferta=venda, ong=ong, quantidade=40, situacao='recebida', quantidade_recebida=38)
        Reserva.objects.create(oferta=doacao, ong=ong, quantidade=20, situacao='recebida', quantidade_recebida=20)
        Reserva.objects.create(oferta=doacao, ong=ong, quantidade=10, situacao='ativa')  # ainda não conta
        Reserva.objects.create(oferta=em_unidades, ong=ong, quantidade=10, situacao='recebida', quantidade_recebida=10)

    def test_indicadores(self):
        from painel.services import indicadores
        resultado = indicadores()
        self.assertEqual(_valor(resultado, 'kg_salvos'), Decimal('58'))         # RN-08, P-01: só kg
        self.assertEqual(_valor(resultado, 'familias_atendidas'), 240)          # RN-10
        self.assertEqual(_valor(resultado, 'renda_gerada'), Decimal('95.00'))   # RN-09: 38 × 2,50
        self.assertEqual(_valor(resultado, 'ongs_ativas'), 2)                   # RN-11
