from django.contrib.auth import get_user_model
from django.test import TestCase

from core.tests.fabricas import criar_usuario


class UsuarioTest(TestCase):
    def test_projeto_usa_o_usuario_proprio(self):
        self.assertEqual(get_user_model()._meta.label, 'contas.Usuario')  # ADR-002

    def test_conta_nasce_como_pessoa(self):
        self.assertEqual(criar_usuario().tipo_conta, 'pessoa')
