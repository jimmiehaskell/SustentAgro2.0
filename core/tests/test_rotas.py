"""Toda tela do site precisa abrir. Se este teste quebrar, alguma tela parou de funcionar."""
from django.test import TestCase, override_settings
from django.urls import reverse

TELAS = [
    ('core:inicio', {}),
    ('ongs:lista', {}),
    ('ongs:detalhe', {'pk': 1}),
    ('contas:cadastro', {}),
    ('contas:cadastro_perfil', {'tipo': 'ong'}),
    ('contas:entrar', {}),
    ('colheita:publicar', {}),
    ('colheita:ofertas', {}),
    ('painel:painel', {}),
    ('ongs:minha_ong', {}),
    ('ongs:necessidades', {}),
    ('colheita:minhas_reservas', {}),
    ('doacoes:a_confirmar', {}),
    ('colheita:minhas_ofertas', {}),
    ('contas:contribuicoes', {}),
    ('doacoes:contribuir', {'ong_pk': 1, 'tipo': 'dinheiro'}),
]


class TelasAbremTest(TestCase):
    def test_todas_as_telas_abrem(self):
        for nome, kwargs in TELAS:
            with self.subTest(tela=nome):
                resposta = self.client.get(reverse(nome, kwargs=kwargs))
                self.assertEqual(resposta.status_code, 200)

    def test_saude_responde_ok(self):
        resposta = self.client.get(reverse('core:saude'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.content, b'ok')

    def test_ong_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse('ongs:detalhe', kwargs={'pk': 999})).status_code, 404)

    def test_filtros_da_lista_e_das_ofertas(self):
        self.assertEqual(self.client.get(reverse('ongs:lista') + '?ods=2&q=sopa').status_code, 200)
        self.assertEqual(self.client.get(reverse('colheita:ofertas') + '?dist=30').status_code, 200)

    def test_minha_conta_de_visitante_leva_ao_login(self):
        resposta = self.client.get(reverse('contas:minha_conta'))
        self.assertRedirects(resposta, reverse('contas:entrar'))


class PerfilMockTest(TestCase):
    @override_settings(DEBUG=True)
    def test_perfil_simulado_muda_o_menu_da_colheita(self):
        self.client.get(reverse('core:perfil_mock', kwargs={'perfil': 'agricultor'}))
        resposta = self.client.get(reverse('core:inicio'))
        self.assertEqual(resposta.context['perfil'], 'agricultor')
        self.assertEqual(resposta.context['url_colheita'], 'colheita:publicar')  # D-26, RN-25

    @override_settings(DEBUG=True)
    def test_ong_simulada_ve_a_versao_com_reserva(self):
        self.client.get(reverse('core:perfil_mock', kwargs={'perfil': 'ong'}))
        resposta = self.client.get(reverse('colheita:ofertas'))
        self.assertTrue(resposta.context['versao_ong'])
        self.assertContains(resposta, 'Reservar')

    def test_perfil_simulado_nao_existe_fora_do_debug(self):
        resposta = self.client.get(reverse('core:perfil_mock', kwargs={'perfil': 'ong'}))
        self.assertEqual(resposta.status_code, 404)
