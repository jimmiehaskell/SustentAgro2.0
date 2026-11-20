"""Contratos e validações dos models da BL-24."""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contas.choices import TipoConta
from contas.models import Localidade, PerfilPessoa, Usuario
from core.tests.fabricas import criar_agricultor, criar_doador, criar_localidade, criar_usuario


class LocalidadeTest(TestCase):
    def test_nome_e_unico_no_banco(self):
        localidade = criar_localidade()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Localidade.objects.create(
                nome=localidade.nome, uf='GO', latitude='-15.000000', longitude='-48.000000')

    def test_localidades_sao_ordenadas_por_nome(self):
        criar_localidade('Ceilândia')
        criar_localidade('Brazlândia')
        self.assertQuerySetEqual(
            Localidade.objects.all(), ['Brazlândia', 'Ceilândia'], transform=lambda loc: loc.nome)

    def test_localidade_em_uso_nao_pode_ser_excluida(self):
        perfil = criar_agricultor()
        with self.assertRaises(ProtectedError):
            perfil.localidade.delete()
        self.assertTrue(Localidade.objects.filter(pk=perfil.localidade_id).exists())

    def test_uf_deve_pertencer_as_choices_existentes(self):
        localidade = criar_localidade()
        localidade.uf = 'XX'
        with self.assertRaises(ValidationError) as erro:
            localidade.full_clean()
        self.assertIn('uf', erro.exception.message_dict)


class ValidacaoPerfilPessoaTest(TestCase):
    def test_usuario_so_pode_ter_um_perfil(self):
        perfil = criar_doador()
        with self.assertRaises(IntegrityError), transaction.atomic():
            PerfilPessoa.objects.create(usuario=perfil.usuario, nome_completo='Outra pessoa')

    def test_mesma_conta_pode_acumular_os_dois_perfis(self):
        perfil = criar_agricultor(eh_doador=True)
        perfil.full_clean()
        perfil.refresh_from_db()
        self.assertTrue(perfil.eh_doador)
        self.assertTrue(perfil.eh_agricultor)
        self.assertEqual(perfil.usuario.perfil_pessoa, perfil)

    def test_conta_ong_nao_pode_ter_perfil_pessoa(self):
        perfil = PerfilPessoa(usuario=criar_usuario(TipoConta.ONG), nome_completo='Pessoa')
        with self.assertRaises(ValidationError) as erro:
            perfil.full_clean()
        self.assertIn('usuario', erro.exception.message_dict)

    def test_agricultor_precisa_de_localidade_mesmo_sendo_doador(self):
        for eh_doador in (False, True):
            with self.subTest(eh_doador=eh_doador):
                perfil = PerfilPessoa(
                    usuario=criar_usuario(), nome_completo='Pessoa',
                    eh_agricultor=True, eh_doador=eh_doador)
                with self.assertRaises(ValidationError) as erro:
                    perfil.full_clean()
                self.assertIn('localidade', erro.exception.message_dict)

    def test_doador_pode_ficar_sem_localidade_e_telefone(self):
        perfil = criar_doador()
        perfil.full_clean()
        self.assertIsNone(perfil.localidade)
        self.assertEqual(perfil.telefone, '')

    def test_localidade_acessa_seus_perfis(self):
        perfil = criar_agricultor()
        self.assertQuerySetEqual(perfil.localidade.perfis.all(), [perfil])

    def test_excluir_usuario_exclui_perfil_e_preserva_localidade(self):
        perfil = criar_agricultor()
        perfil.usuario.delete()
        self.assertFalse(PerfilPessoa.objects.filter(pk=perfil.pk).exists())
        self.assertTrue(Localidade.objects.filter(pk=perfil.localidade_id).exists())

    def test_rotulos_em_portugues_no_admin(self):
        self.assertEqual(str(PerfilPessoa._meta.verbose_name), 'perfil de pessoa')
        self.assertEqual(str(PerfilPessoa._meta.verbose_name_plural), 'perfis de pessoa')
        self.assertEqual(str(PerfilPessoa._meta.get_field('eh_doador').verbose_name),
                         'doador(a) ou voluntário(a)')
        self.assertEqual(str(PerfilPessoa._meta.get_field('eh_agricultor').verbose_name), 'agricultor(a)')


class AdminContasTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = Usuario.objects.create_superuser(username='administrador', password='senha-teste')
        cls.pessoa = criar_usuario()
        cls.ong = criar_usuario(TipoConta.ONG)

    def formulario_perfil(self, **campos):
        requisicao = RequestFactory().get('/admin/')
        requisicao.user = self.administrador
        formulario = admin.site.get_model_admin(PerfilPessoa).get_form(requisicao)
        dados = {'usuario': self.pessoa.pk, 'nome_completo': 'Pessoa', 'eh_doador': True}
        dados.update(campos)
        return formulario(data=dados)

    def test_admin_recusa_perfil_de_conta_ong(self):
        formulario = self.formulario_perfil(usuario=self.ong.pk)
        self.assertFalse(formulario.is_valid())
        self.assertIn('usuario', formulario.errors)

    def test_admin_recusa_agricultor_sem_localidade(self):
        formulario = self.formulario_perfil(eh_agricultor=True)
        self.assertFalse(formulario.is_valid())
        self.assertIn('localidade', formulario.errors)

    def test_admin_aceita_doador_sem_localidade(self):
        formulario = self.formulario_perfil()
        self.assertTrue(formulario.is_valid(), formulario.errors)
        perfil = formulario.save()
        self.assertIsNone(perfil.localidade)

    def test_admin_informa_usuario_obrigatorio_sem_excecao(self):
        formulario = self.formulario_perfil(usuario='')
        self.assertFalse(formulario.is_valid())
        self.assertIn('usuario', formulario.errors)

    def test_administrador_cadastra_e_edita_localidade(self):
        self.client.force_login(self.administrador)
        dados = {'nome': 'Localidade de teste', 'uf': 'DF',
                 'latitude': '-15.819700', 'longitude': '-48.108300'}
        resposta = self.client.post(reverse('admin:contas_localidade_add'), dados)
        self.assertEqual(resposta.status_code, 302)
        localidade = Localidade.objects.get(nome=dados['nome'])
        dados['nome'] = 'Localidade atualizada'
        resposta = self.client.post(reverse('admin:contas_localidade_change', args=[localidade.pk]), dados)
        self.assertEqual(resposta.status_code, 302)
        localidade.refresh_from_db()
        self.assertEqual(localidade.nome, dados['nome'])
