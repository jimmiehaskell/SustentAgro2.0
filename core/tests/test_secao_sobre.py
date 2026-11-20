"""BL-23 (Pedro): seção "Sobre" da Tela 1. RF-34, P-09."""
from django.test import TestCase
from django.urls import reverse


class SecaoSobreTest(TestCase):
    def test_mostra_texto_do_projeto_e_equipe(self):
        resposta = self.client.get(reverse('core:inicio'))
        self.assertContains(resposta, 'Equipe do projeto')
        self.assertContains(resposta, 'Itinerário 5')
        self.assertContains(resposta, 'Pedro Freire de Farias')
        self.assertContains(resposta, 'Vitor Gomes Araújo')
        self.assertNotContains(resposta, 'Vitor Hugo Alves da Silva')  # P-09: saiu da lista