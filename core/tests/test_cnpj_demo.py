"""BL-27 (Pedro): CNPJs da carga de demonstração. RN-24, E-11."""
from django.test import SimpleTestCase

from core.demo.cnpj import digitos_verificadores, gerar_cnpj


class CnpjDemoTest(SimpleTestCase):
    def test_digitos_de_um_cnpj_conhecido(self):
        self.assertEqual(digitos_verificadores('112223330001'), '81')   # 11.222.333/0001-81

    def test_cnpj_gerado_tem_14_digitos_e_digitos_certos(self):
        cnpj = gerar_cnpj(1)
        self.assertEqual(len(cnpj), 14)
        self.assertTrue(cnpj.isdigit())
        self.assertEqual(cnpj[12:], digitos_verificadores(cnpj[:12]))

    def test_numeros_diferentes_geram_cnpjs_diferentes(self):  # RN-24: únicos
        cnpjs = [gerar_cnpj(n) for n in range(1, 501)]
        self.assertEqual(len(set(cnpjs)), 500)

    def test_numero_fora_da_faixa(self):
        with self.assertRaises(ValueError):
            gerar_cnpj(0)
