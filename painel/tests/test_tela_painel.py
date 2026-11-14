"""BL-20 e BL-37 (Pedro): Tela 8 · Painel de impacto com os números do banco. RF-29, RF-30, RF-31."""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse

from colheita.models import Reserva
from core.tests.fabricas import criar_oferta, criar_ong

BRASILIA = ZoneInfo('America/Sao_Paulo')


class TelaPainelTest(TestCase):
    def setUp(self):
        ong = criar_ong(familias_por_mes=180, ods=(1, 2))
        venda = criar_oferta(quantidade='5000', destino='vender', preco_unitario='2.50')
        Reserva.objects.create(oferta=venda, ong=ong, quantidade=4380, situacao='recebida',
                               quantidade_recebida=4380, recebida_em=datetime(2026, 10, 10, 10, tzinfo=BRASILIA))

    def test_mostra_indicadores_grafico_e_ods(self):
        resposta = self.client.get(reverse('painel:painel'))
        self.assertContains(resposta, '4.380 kg')              # RF-29, no formato brasileiro
        self.assertContains(resposta, 'R$ 10.950,00')          # 4.380 × 2,50
        self.assertContains(resposta, 'id="dados-kg-por-mes"')  # RF-30
        self.assertContains(resposta, '[["out", "4380.0"]]')    # o mês vem do banco, no horário de Brasília
        self.assertContains(resposta, 'chart.umd.min.js')
        self.assertContains(resposta, 'das ações confirmadas')  # RF-31
        self.assertNotContains(resposta, 'Tela em construção')


class TelaPainelVaziaTest(TestCase):
    def test_estado_vazio_sem_reservas_recebidas(self):
        resposta = self.client.get(reverse('painel:painel'))
        self.assertContains(resposta, 'Ainda não há colheitas recebidas')
        self.assertContains(resposta, 'Sem ações confirmadas ainda.')
        self.assertContains(resposta, 'R$ 0,00')
        self.assertNotContains(resposta, 'chart.umd.min.js')
