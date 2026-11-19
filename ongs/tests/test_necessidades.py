"""BL-41 (Júlia): gestão de necessidades pela ONG. RF-13, RN-21, UC-04, RNF-05."""
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from core.tests.fabricas import criar_ong
from ongs.models import Necessidade
from ongs.services import criar_necessidade, editar_necessidade, encerrar_necessidade


def _necessidade(ong, titulo='Cestas básicas', meta='60', **campos):
    return Necessidade.objects.create(ong=ong, titulo=titulo, tipo=campos.pop('tipo', 'itens'),
                                      unidade=campos.pop('unidade', 'cestas'), meta=Decimal(meta), **campos)


class GestaoDeNecessidadeTest(TestCase):  # RF-13, RN-21, UC-04
    def _confirmado(self, valor):
        return patch('ongs.services.confirmado_da_necessidade', return_value=Decimal(valor))

    def _dados(self, **campos):
        return {'titulo': 'Cestas básicas', 'descricao': '', 'tipo': 'itens', 'unidade': 'cestas',
                'meta': '60', **campos}

    def test_criar_necessidade_nasce_aberta_e_da_ong(self):
        ong = criar_ong()
        necessidade = criar_necessidade(ong, self._dados())
        necessidade.refresh_from_db()
        self.assertEqual((necessidade.ong, necessidade.situacao, necessidade.meta), (ong, 'aberta', Decimal('60')))

    def test_criar_recusa_dado_invalido(self):
        for campo, valor in (('meta', '0'), ('meta', 'abc'), ('tipo', 'voluntarios'), ('titulo', '')):
            with self.subTest(campo=campo, valor=valor):
                with self.assertRaises(ValidationError) as erro:
                    criar_necessidade(criar_ong(), self._dados(**{campo: valor}))
                self.assertIn(campo, erro.exception.message_dict)
        self.assertFalse(Necessidade.objects.exists())

    def test_editar_titulo_e_meta(self):
        necessidade = _necessidade(criar_ong(), meta='60')
        editar_necessidade(necessidade, {'titulo': 'Gás de cozinha', 'meta': '80'})
        necessidade.refresh_from_db()
        self.assertEqual((necessidade.titulo, necessidade.meta), ('Gás de cozinha', Decimal('80')))

    def test_meta_menor_que_o_confirmado_e_recusada(self):
        necessidade = _necessidade(criar_ong(), meta='60')
        with self._confirmado('30'), self.assertRaises(ValidationError) as erro:
            editar_necessidade(necessidade, {'meta': '20'})
        self.assertIn('meta', erro.exception.message_dict)
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.meta, Decimal('60'))

    def test_meta_igual_ao_confirmado_e_aceita(self):
        necessidade = _necessidade(criar_ong(), meta='60')
        with self._confirmado('30'):
            editar_necessidade(necessidade, {'meta': '30'})
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'atendida')

    def test_bater_a_meta_deixa_atendida(self):
        necessidade = _necessidade(criar_ong(), meta='60')
        with self._confirmado('60'):
            editar_necessidade(necessidade, {})
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'atendida')
        self.assertFalse(necessidade.aceita_contribuicoes)

    def test_aumentar_a_meta_reabre(self):
        necessidade = _necessidade(criar_ong(), meta='60', situacao='atendida')
        with self._confirmado('60'):
            editar_necessidade(necessidade, {'meta': '100'})
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'aberta')
        self.assertTrue(necessidade.aceita_contribuicoes)

    def test_encerrar(self):
        necessidade = _necessidade(criar_ong())
        encerrar_necessidade(necessidade)
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'encerrada')
        self.assertFalse(necessidade.aceita_contribuicoes)

    def test_encerrada_continua_encerrada_ao_editar(self):
        necessidade = _necessidade(criar_ong(), meta='60', situacao='encerrada')
        with self._confirmado('60'):
            editar_necessidade(necessidade, {'meta': '100'})
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'encerrada')

    def test_save_nao_recalcula_a_situacao(self):  # regressão: o ponto 2 da revisão
        necessidade = _necessidade(criar_ong(), meta='60', situacao='atendida')
        necessidade.save()
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'atendida')


class NecessidadesDaOngTelaTest(TestCase):  # RF-13, UC-04, RNF-05
    def setUp(self):
        self.ong = criar_ong()
        self.client.force_login(self.ong.usuario)
        self.url = reverse('ongs:necessidades')

    def _post(self, **dados):
        return self.client.post(self.url, dados, follow=True)

    def test_lista_so_as_necessidades_da_propria_ong(self):
        _necessidade(self.ong, 'Cestas básicas')
        _necessidade(criar_ong(), 'Gás de cozinha')
        resposta = self.client.get(self.url)
        self.assertContains(resposta, 'Cestas básicas')
        self.assertNotContains(resposta, 'Gás de cozinha')

    def test_criar(self):
        self._post(acao='criar', titulo='Cestas básicas', tipo='itens', unidade='cestas', meta='60')
        necessidade = self.ong.necessidades.get()
        self.assertEqual((necessidade.titulo, necessidade.meta, necessidade.situacao),
                         ('Cestas básicas', Decimal('60'), 'aberta'))

    def test_criar_com_dado_invalido_nao_grava(self):
        resposta = self._post(acao='criar', titulo='', tipo='itens', unidade='cestas', meta='abc')
        self.assertFalse(self.ong.necessidades.exists())
        self.assertTrue(list(resposta.context['messages']))

    def test_editar_titulo_e_meta(self):
        necessidade = _necessidade(self.ong, meta='60')
        self._post(acao='editar', necessidade=necessidade.pk, titulo='Gás de cozinha', meta='80,5')
        necessidade.refresh_from_db()
        self.assertEqual((necessidade.titulo, necessidade.meta), ('Gás de cozinha', Decimal('80.5')))

    def test_meta_menor_que_o_confirmado_e_recusada_pela_tela(self):
        necessidade = _necessidade(self.ong, meta='60')
        with patch('ongs.services.confirmado_da_necessidade', return_value=Decimal('30')):
            resposta = self._post(acao='editar', necessidade=necessidade.pk, meta='20')
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.meta, Decimal('60'))
        mensagens = [str(m) for m in resposta.context['messages']]
        self.assertTrue(any('A meta não pode ser menor' in m for m in mensagens))

    def test_encerrar(self):
        necessidade = _necessidade(self.ong)
        self._post(acao='encerrar', necessidade=necessidade.pk)
        necessidade.refresh_from_db()
        self.assertEqual(necessidade.situacao, 'encerrada')

    def test_necessidade_de_outra_ong_da_404(self):  # RNF-05
        alheia = _necessidade(criar_ong(), 'Gás de cozinha', meta='60')
        for acao in ('editar', 'encerrar'):
            with self.subTest(acao=acao):
                resposta = self.client.post(self.url, {'acao': acao, 'necessidade': alheia.pk, 'titulo': 'X'})
                self.assertEqual(resposta.status_code, 404)
        alheia.refresh_from_db()
        self.assertEqual((alheia.titulo, alheia.situacao), ('Gás de cozinha', 'aberta'))

    def test_visitante_vai_para_o_login(self):
        self.client.logout()
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resposta.url)

    def test_ong_pendente_recebe_403(self):  # RN-01: só ONG ativa gerencia necessidades
        self.client.force_login(criar_ong(situacao='pendente').usuario)
        self.assertEqual(self.client.get(self.url).status_code, 403)
