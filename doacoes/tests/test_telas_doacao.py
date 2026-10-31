"""BL-22 (Pedro): Tela 12 · Doações a confirmar e Tela 15 · Contribuir, em mock. RF-14 a RF-17."""
from django.test import TestCase
from django.urls import reverse


class TelaContribuirTest(TestCase):
    def _abrir(self, tipo, ong_pk=1):
        return self.client.get(reverse('doacoes:contribuir', args=[ong_pk, tipo]))

    def test_doar_itens(self):  # RF-14
        resposta = self._abrir('itens')
        self.assertContains(resposta, 'Registrar promessa de doação')
        self.assertContains(resposta, 'Cestas básicas · faltam 18 cestas')   # protótipo: quanto falta
        self.assertNotContains(resposta, 'Tela em construção')

    def test_ser_voluntario(self):  # RF-15
        resposta = self._abrir('voluntariado')
        self.assertContains(resposta, 'Quero me inscrever')

    def test_doar_dinheiro_mostra_a_chave_pix(self):  # RF-17
        resposta = self._abrir('dinheiro')
        self.assertContains(resposta, 'pix@solnascente.org.br')
        self.assertContains(resposta, 'Doação livre à ONG')

    def test_tipo_invalido_da_404(self):
        self.assertEqual(self._abrir('outra-coisa').status_code, 404)

    def test_tipo_que_a_ong_nao_aceita_da_404(self):  # UC-07
        self.assertEqual(self._abrir('dinheiro', ong_pk=2).status_code, 404)


class TelaAConfirmarTest(TestCase):
    def test_lista_promessas_e_inscricoes_pendentes(self):  # RF-16
        resposta = self.client.get(reverse('doacoes:a_confirmar'))
        self.assertContains(resposta, 'Mariana Costa')
        self.assertContains(resposta, 'Inscrição pendente')
        self.assertContains(resposta, 'R$ 50,00')
        self.assertContains(resposta, 'Recusar')
        self.assertNotContains(resposta, 'Tela em construção')
