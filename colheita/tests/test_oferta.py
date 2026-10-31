"""BL-32 (Gabriel): RN-13, RN-16, UC-08. Remova o @skip ao implementar colheita.services.validar_oferta."""
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from colheita.services import validar_oferta


def _oferta(**campos):
    padrao = dict(quantidade=Decimal('40'), unidade='kg', destino='doar', preco_unitario=None,
                  colher_ate=date.today() + timedelta(days=3))
    padrao.update(campos)
    return SimpleNamespace(**padrao)


class ValidarOfertaTest(SimpleTestCase):
    def test_doacao_valida(self):
        validar_oferta(_oferta())  # não levanta erro

    def test_venda_sem_preco_e_recusada(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(destino='vender'))

    def test_doacao_com_preco_e_recusada(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(preco_unitario=Decimal('2.50')))

    def test_venda_com_preco_e_aceita(self):
        validar_oferta(_oferta(destino='vender', preco_unitario=Decimal('2.50')))

    def test_kg_aceita_uma_casa_decimal(self):
        validar_oferta(_oferta(quantidade=Decimal('12.5')))  # E-01

    def test_unidade_nao_aceita_fracao(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(unidade='un', quantidade=Decimal('12.5')))

    def test_colher_ate_no_passado_e_recusado(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(colher_ate=date.today() - timedelta(days=1)))


class ValidarOfertaLimitesTest(SimpleTestCase):
    """Limites além do contrato do BL-32: RN-16/E-01 em kg e valores que precisam ser positivos."""

    def test_kg_nao_aceita_duas_casas_decimais(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(quantidade=Decimal('12.55')))  # E-01

    def test_unidade_inteira_e_aceita(self):
        validar_oferta(_oferta(unidade='un', quantidade=Decimal('30')))

    def test_quantidade_zero_e_recusada(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(quantidade=Decimal('0')))

    def test_venda_com_preco_zero_e_recusada(self):
        with self.assertRaises(ValidationError):
            validar_oferta(_oferta(destino='vender', preco_unitario=Decimal('0')))

    def test_colher_ate_hoje_e_aceito(self):
        validar_oferta(_oferta(colher_ate=date.today()))

    def test_erros_vem_por_campo(self):
        with self.assertRaises(ValidationError) as ctx:
            validar_oferta(_oferta(destino='vender', colher_ate=date.today() - timedelta(days=1)))
        self.assertEqual(set(ctx.exception.message_dict), {'preco_unitario', 'colher_ate'})
