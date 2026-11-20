"""BL-29 (Vinicius): RF-10."""
from django.test import SimpleTestCase

from ongs.services import validar_cnpj


class ValidarCnpjTest(SimpleTestCase):
    def test_cnpj_valido_com_e_sem_pontuacao(self):
        self.assertTrue(validar_cnpj('11.222.333/0001-81'))
        self.assertTrue(validar_cnpj('11222333000181'))

    def test_digito_verificador_errado(self):
        self.assertFalse(validar_cnpj('11.222.333/0001-80'))

    def test_sequencia_repetida_e_invalida(self):
        self.assertFalse(validar_cnpj('00.000.000/0000-00'))
        self.assertFalse(validar_cnpj('11111111111111'))

    def test_tamanho_errado(self):
        self.assertFalse(validar_cnpj('1122233300018'))
        self.assertFalse(validar_cnpj(''))
