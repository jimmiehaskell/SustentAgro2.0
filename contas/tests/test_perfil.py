"""BL-24 (Vinicius): RN-12. Remova o @skip quando os models PerfilPessoa e Localidade existirem."""
from unittest import skip

from django.test import TestCase

from core.perfis import perfil_da_requisicao
from core.tests.fabricas import criar_agricultor, criar_doador


class _Requisicao:
    def __init__(self, usuario):
        self.user = usuario
        self.session = {}


@skip('Remova ao implementar o BL-24')
class PerfilPessoaTest(TestCase):
    def test_agricultor_tem_precedencia_quando_tem_os_dois_perfis(self):
        perfil = criar_agricultor(eh_doador=True)  # RN-12, RN-25
        self.assertEqual(perfil_da_requisicao(_Requisicao(perfil.usuario)), 'agricultor')

    def test_doador_e_pessoa(self):
        perfil = criar_doador()
        self.assertEqual(perfil_da_requisicao(_Requisicao(perfil.usuario)), 'pessoa')

    def test_usuario_acessa_o_perfil_pelo_related_name(self):
        perfil = criar_agricultor()
        self.assertEqual(perfil.usuario.perfil_pessoa, perfil)
