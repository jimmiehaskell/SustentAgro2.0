"""BL-38: destino do menu Colheita Solidária (D-26, RN-25, E-12)."""
from django.test import TestCase, override_settings
from django.urls import reverse

from core.tests.fabricas import criar_agricultor, criar_doador, criar_ong


class DestinoColheitaTest(TestCase):
    def conferir_destino(self, destino):
        resposta = self.client.get(reverse('core:inicio'))
        self.assertEqual(resposta.context['url_colheita'], destino)
        self.assertContains(resposta, f'href="{reverse(destino)}">Colheita Solidária</a>')

    def test_visitante_vai_para_lista(self):
        self.conferir_destino('colheita:ofertas')

    def test_doador_vai_para_lista(self):
        self.client.force_login(criar_doador().usuario)
        self.conferir_destino('colheita:ofertas')

    def test_ong_vai_para_lista(self):
        self.client.force_login(criar_ong().usuario)
        self.conferir_destino('colheita:ofertas')

    def test_agricultor_vai_para_publicacao(self):
        self.client.force_login(criar_agricultor().usuario)
        self.conferir_destino('colheita:publicar')

    def test_doador_e_agricultor_vai_para_publicacao_com_link_para_lista(self):
        self.client.force_login(criar_agricultor(eh_doador=True).usuario)
        self.conferir_destino('colheita:publicar')
        resposta = self.client.get(reverse('colheita:publicar'))
        lista = reverse('colheita:ofertas')
        self.assertContains(resposta, f'href="{lista}">Ver a lista de ofertas</a>')

    @override_settings(DEBUG=True)
    def test_perfis_simulados_preservam_destino(self):
        for perfil, destino in (
            ('visitante', 'colheita:ofertas'),
            ('pessoa', 'colheita:ofertas'),
            ('ong', 'colheita:ofertas'),
            ('agricultor', 'colheita:publicar'),
        ):
            with self.subTest(perfil=perfil):
                self.client.get(reverse('core:perfil_mock', args=[perfil]))
                self.conferir_destino(destino)
