"""BL-42: regras de registro e integração da promessa/inscrição."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from contas.models import PerfilPessoa
from core.perfis import CHAVE_SESSAO_MOCK
from core.tests.fabricas import criar_agricultor, criar_doador, criar_ong
from doacoes.models import Contribuicao
from doacoes.services import registrar_contribuicao
from ongs.models import Necessidade, Ong


class ContribuicaoTest(TestCase):
    def setUp(self):
        self.pessoa = criar_doador()
        self.ong = criar_ong()
        self.ong.aceita_itens = True
        self.ong.aceita_voluntariado = True
        self.ong.save(update_fields=['aceita_itens', 'aceita_voluntariado'])
        self.itens = Necessidade.objects.create(ong=self.ong, titulo='Cestas', tipo='itens',
                                                unidade='cestas', meta=50)
        self.voluntariado = Necessidade.objects.create(ong=self.ong, titulo='Ajudantes', tipo='voluntariado',
                                                       unidade='pessoas', meta=10)

    def test_itens_pendentes_nao_movem_barra(self):
        contribuicao = registrar_contribuicao(self.pessoa, self.ong, 'itens', '15.25', self.itens)
        self.assertEqual(contribuicao.quantidade, Decimal('15.25'))
        self.assertEqual(contribuicao.situacao, 'pendente')
        self.assertEqual((contribuicao.pessoa, contribuicao.ong, contribuicao.necessidade),
                         (self.pessoa, self.ong, self.itens))
        self.assertIsNone(contribuicao.quantidade_confirmada)
        self.assertIsNone(contribuicao.confirmada_em)
        self.assertEqual(self.itens.confirmado, 0)
        self.assertEqual(self.itens.percentual, 0)

    def test_voluntariado_pendente_nao_move_barra(self):
        contribuicao = registrar_contribuicao(self.pessoa, self.ong, 'voluntariado', 1, self.voluntariado)
        self.assertEqual(contribuicao.quantidade, 1)
        self.assertEqual(contribuicao.situacao, 'pendente')
        self.assertEqual(self.voluntariado.confirmado, 0)
        self.assertEqual(self.voluntariado.percentual, 0)

    def test_somente_confirmadas_entram_no_progresso(self):
        Contribuicao.objects.create(pessoa=self.pessoa, ong=self.ong, necessidade=self.itens,
                                    tipo='itens', quantidade=10, quantidade_confirmada=10,
                                    situacao='confirmada')
        self.assertEqual(self.itens.percentual, 20)
        registrar_contribuicao(self.pessoa, self.ong, 'itens', 15, self.itens)
        self.assertEqual(self.itens.confirmado, 10)
        self.assertEqual(self.itens.percentual, 20)

    def test_necessidade_com_contribuicao_nao_pode_ser_excluida(self):
        registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)
        with self.assertRaises(ProtectedError):
            self.itens.delete()

    def test_quantidades_invalidas(self):
        for valor in ('0', '-1', 'abc', 'NaN', 'Infinity', '1.123', '100000000'):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                registrar_contribuicao(self.pessoa, self.ong, 'itens', valor, self.itens)
        self.assertFalse(Contribuicao.objects.exists())

    def test_voluntariado_e_individual(self):
        with self.assertRaises(ValidationError):
            registrar_contribuicao(self.pessoa, self.ong, 'voluntariado', 2, self.voluntariado)

    def test_rejeita_tipo_financeiro_e_sem_necessidade(self):
        for tipo in ('dinheiro', 'invalido'):
            with self.subTest(tipo=tipo), self.assertRaises(ValidationError):
                registrar_contribuicao(self.pessoa, self.ong, tipo, 1, self.itens)
        for tipo in ('itens', 'voluntariado'):
            with self.subTest(tipo=tipo), self.assertRaises(ValidationError):
                registrar_contribuicao(self.pessoa, self.ong, tipo, 1)

    def test_rejeita_ong_inativa_e_ajuda_nao_aceita(self):
        self.ong.situacao = 'pendente'
        self.ong.save(update_fields=['situacao'])
        with self.assertRaises(ValidationError):
            registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)
        self.ong.situacao = 'ativa'
        self.ong.aceita_itens = False
        self.ong.save(update_fields=['situacao', 'aceita_itens'])
        with self.assertRaises(ValidationError):
            registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)

    def test_estado_atual_da_ong_prevalece_sobre_objeto_antigo(self):
        Ong.objects.filter(pk=self.ong.pk).update(situacao='desativada')
        with self.assertRaises(ValidationError):
            registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)

    def test_rejeita_necessidade_de_outra_ong_ou_tipo(self):
        outra = criar_ong()
        necessidade = Necessidade.objects.create(ong=outra, titulo='Outra', tipo='itens', unidade='un', meta=5)
        for escolhida in (necessidade, self.voluntariado):
            with self.subTest(pk=escolhida.pk), self.assertRaises(ValidationError):
                registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, escolhida)

    def test_rejeita_necessidade_nao_aberta(self):
        for situacao in ('atendida', 'encerrada'):
            with self.subTest(situacao=situacao):
                self.itens.situacao = situacao
                self.itens.save(update_fields=['situacao'])
                with self.assertRaises(ValidationError):
                    registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)

    def test_rejeita_perfil_sem_doador(self):
        agricultor = criar_agricultor()
        with self.assertRaises(ValidationError):
            registrar_contribuicao(agricultor, self.ong, 'itens', 1, self.itens)

    def test_dados_do_perfil_no_banco_prevalecem_sobre_objeto_modificado(self):
        self.pessoa.eh_doador = False
        PerfilPessoa.objects.filter(pk=self.pessoa.pk).update(eh_doador=False)
        with self.assertRaises(ValidationError):
            registrar_contribuicao(self.pessoa, self.ong, 'itens', 1, self.itens)

    def test_post_itens_registra_e_redireciona(self):
        outra_pessoa = criar_doador()
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        resposta = self.client.post(url, {'necessidade': self.itens.pk, 'quantidade': '15',
                                          'pessoa': outra_pessoa.pk}, follow=True)
        self.assertRedirects(resposta, url)
        self.assertContains(resposta, 'Promessa registrada')
        self.assertEqual(Contribuicao.objects.get().quantidade, 15)
        self.assertEqual(Contribuicao.objects.get().pessoa, self.pessoa)

    def test_post_voluntariado_registra(self):
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'voluntariado'])
        resposta = self.client.post(url, {'necessidade': self.voluntariado.pk}, follow=True)
        self.assertRedirects(resposta, url)
        self.assertContains(resposta, 'Inscrição registrada')
        self.assertEqual(Contribuicao.objects.get().quantidade, 1)

    def test_visitante_vai_ao_login(self):
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        resposta = self.client.post(url, {'necessidade': self.itens.pk, 'quantidade': '1'})
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('next=', resposta['Location'])
        self.assertFalse(Contribuicao.objects.exists())

    @override_settings(DEBUG=True)
    def test_mock_nao_autoriza_ong_a_gravar(self):
        self.client.force_login(self.ong.usuario)
        sessao = self.client.session
        sessao[CHAVE_SESSAO_MOCK] = 'pessoa'
        sessao.save()
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        self.assertEqual(self.client.post(url, {'necessidade': self.itens.pk, 'quantidade': 1}).status_code, 403)
        self.assertFalse(Contribuicao.objects.exists())

    def test_post_invalido_nao_grava(self):
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        for dados in ({'necessidade': self.itens.pk, 'quantidade': 'abc'},
                      {'necessidade': self.voluntariado.pk, 'quantidade': '1'}):
            with self.subTest(dados=dados):
                resposta = self.client.post(url, dados)
                self.assertEqual(resposta.status_code, 200)
                self.assertContains(resposta, 'alert-danger')
                self.assertFalse(Contribuicao.objects.exists())

    def test_post_necessidade_de_outra_ong_nao_grava(self):
        outra = criar_ong()
        necessidade = Necessidade.objects.create(ong=outra, titulo='Outra', tipo='itens', unidade='un', meta=5)
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        resposta = self.client.post(url, {'necessidade': necessidade.pk, 'quantidade': 1})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'alert-danger')
        self.assertFalse(Contribuicao.objects.exists())

    def test_post_necessidade_encerrada_nao_grava(self):
        self.itens.situacao = 'encerrada'
        self.itens.save(update_fields=['situacao'])
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        resposta = self.client.post(url, {'necessidade': self.itens.pk, 'quantidade': 1})
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Contribuicao.objects.exists())

    def test_ong_inativa_nao_exibe_formulario(self):
        self.ong.situacao = 'reprovada'
        self.ong.save(update_fields=['situacao'])
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertFalse(Contribuicao.objects.exists())

    def test_formulario_sem_necessidade_aberta_exibe_aviso(self):
        self.itens.situacao = 'atendida'
        self.itens.save(update_fields=['situacao'])
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        resposta = self.client.get(url)
        self.assertContains(resposta, 'não tem necessidade de itens aberta')
        self.assertNotContains(resposta, 'Registrar promessa de doação')

    def test_necessidade_inexistente_da_404(self):
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'itens'])
        self.assertEqual(self.client.post(url, {'necessidade': 999999, 'quantidade': 1}).status_code, 404)

    def test_tipo_invalido_da_404(self):
        self.client.force_login(self.pessoa.usuario)
        url = reverse('doacoes:contribuir', args=[self.ong.pk, 'invalido'])
        self.assertEqual(self.client.post(url, {'necessidade': self.itens.pk}).status_code, 404)
