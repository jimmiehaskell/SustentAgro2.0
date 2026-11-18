"""BL-28: cadastros, autenticação e integridade transacional."""
from unittest.mock import patch

from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from contas.models import PerfilPessoa, Usuario
from core.perfis import CHAVE_SESSAO_MOCK
from core.tests.fabricas import criar_agricultor, criar_doador, criar_localidade, criar_ods, criar_ong
from ongs.models import Ong


class CadastroTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.localidade = criar_localidade()
        cls.ods = criar_ods()

    def dados(self, tipo='pessoa', **alteracoes):
        dados = {'username': 'nova.conta', 'password1': 'Senha-forte!82x', 'password2': 'Senha-forte!82x',
                 'nome_completo': 'Pessoa de teste', 'email': 'pessoa@example.org', 'telefone': '(61) 99999-1234'}
        if tipo != 'pessoa':
            dados['localidade'] = self.localidade.pk
        if tipo == 'ong':
            dados.update(nome='ONG de teste', nome_curto='ONG teste', cnpj='11.222.333/0001-81',
                         email_contato='ong@example.org', ods=[self.ods.pk], aceita_itens='on')
        dados.update(alteracoes)
        return dados

    def enviar(self, tipo='pessoa', **alteracoes):
        return self.client.post(reverse('contas:cadastro_perfil', args=[tipo]), self.dados(tipo, **alteracoes))

    def assert_sem_cadastro(self):
        self.assertFalse(Usuario.objects.exists())
        self.assertFalse(PerfilPessoa.objects.exists())
        self.assertFalse(Ong.objects.exists())
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_cadastra_doador_sem_localidade_e_autentica(self):
        resposta = self.enviar()
        usuario = Usuario.objects.get()
        self.assertRedirects(resposta, reverse('contas:minha_conta'), fetch_redirect_response=False)
        self.assertEqual(self.client.session['_auth_user_id'], str(usuario.pk))
        self.assertTrue(usuario.check_password('Senha-forte!82x'))
        self.assertEqual(usuario.email, 'pessoa@example.org')
        self.assertEqual(usuario.tipo_conta, 'pessoa')
        self.assertTrue(usuario.perfil_pessoa.eh_doador)
        self.assertFalse(usuario.perfil_pessoa.eh_agricultor)
        self.assertIsNone(usuario.perfil_pessoa.localidade)

    def test_cadastra_doador_com_localidade(self):
        self.enviar(localidade=self.localidade.pk)
        self.assertEqual(PerfilPessoa.objects.get().localidade, self.localidade)

    def test_cadastra_agricultor_e_autentica(self):
        self.enviar('agricultor')
        perfil = PerfilPessoa.objects.get()
        self.assertTrue(perfil.eh_agricultor)
        self.assertFalse(perfil.eh_doador)
        self.assertEqual(perfil.localidade, self.localidade)
        self.assertEqual(self.client.session['_auth_user_id'], str(perfil.usuario_id))

    def test_cadastra_ong_pendente_normaliza_cnpj_e_autentica(self):
        self.enviar('ong', situacao='ativa', is_staff=True, is_superuser=True, tipo_conta='pessoa')
        ong = Ong.objects.get()
        self.assertEqual(ong.cnpj, '11222333000181')
        self.assertEqual(ong.situacao, 'pendente')
        self.assertIsNone(ong.aprovada_em)
        self.assertEqual(ong.usuario.tipo_conta, 'ong')
        self.assertEqual(ong.usuario.email, 'ong@example.org')
        self.assertFalse(ong.usuario.is_staff)
        self.assertFalse(ong.usuario.is_superuser)
        self.assertFalse(PerfilPessoa.objects.exists())
        self.assertQuerySetEqual(ong.ods.all(), [self.ods])
        self.assertTrue(ong.aceita_itens)
        self.assertFalse(ong.aceita_dinheiro)
        self.assertEqual(self.client.session['_auth_user_id'], str(ong.usuario_id))

    def test_localidade_obrigatoria_para_agricultor_e_ong(self):
        for tipo in ('agricultor', 'ong'):
            with self.subTest(tipo=tipo):
                resposta = self.enviar(tipo, localidade='')
                erros = ['Este campo é obrigatório.']
                if tipo == 'agricultor':
                    erros.append('Informe a localidade do agricultor.')
                self.assertFormError(resposta.context['form_perfil'], 'localidade', erros)
                self.assert_sem_cadastro()

    def test_localidade_inexistente_e_rejeitada_em_todos_os_perfis(self):
        for tipo in ('pessoa', 'agricultor', 'ong'):
            with self.subTest(tipo=tipo):
                resposta = self.enviar(tipo, localidade=99999)
                self.assertIn('localidade', resposta.context['form_perfil'].errors)
                self.assert_sem_cadastro()

    def test_ods_obrigatorio_e_existente(self):
        for valor in ([], [99999]):
            with self.subTest(ods=valor):
                resposta = self.enviar('ong', ods=valor)
                self.assertIn('ods', resposta.context['form_perfil'].errors)
                self.assert_sem_cadastro()

    def test_cnpj_invalido(self):
        resposta = self.enviar('ong', cnpj='11.222.333/0001-00')
        self.assertIn('cnpj', resposta.context['form_perfil'].errors)
        self.assert_sem_cadastro()

    def test_duplicidades_ong_nao_criam_usuario(self):
        ong = criar_ong(cnpj='11222333000181')
        for campo, valor in (('cnpj', '11.222.333/0001-81'), ('nome', ong.nome), ('nome_curto', ong.nome_curto)):
            with self.subTest(campo=campo):
                resposta = self.enviar('ong', **{campo: valor})
                self.assertIn(campo, resposta.context['form_perfil'].errors)
                self.assertEqual(Usuario.objects.count(), 1)
                self.assertEqual(Ong.objects.count(), 1)

    def test_username_duplicado(self):
        Usuario.objects.create_user(username='nova.conta')
        resposta = self.enviar()
        self.assertIn('username', resposta.context['form_conta'].errors)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertFalse(PerfilPessoa.objects.exists())

    def test_senhas_fracas_divergentes_e_dados_invalidos(self):
        for alteracoes in ({'password1': '123', 'password2': '123'}, {'password2': 'diferente'},
                           {'email': 'invalido'}, {'nome_completo': ''}, {'username': 'invalido!'}):
            with self.subTest(alteracoes=alteracoes):
                resposta = self.enviar(**alteracoes)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context['form_conta'].errors or resposta.context['form_perfil'].errors)
                self.assert_sem_cadastro()

    def test_senha_semelhante_ao_email_mostra_erro_no_campo(self):
        resposta = self.enviar(email='meuemailmuitolongo@example.org',
                               password1='meuemailmuitolongo', password2='meuemailmuitolongo')
        self.assertIn('password1', resposta.context['form_conta'].errors)
        self.assert_sem_cadastro()

    def test_falha_ao_salvar_perfil_desfaz_usuario(self):
        for tipo, modelo in (('pessoa', PerfilPessoa), ('agricultor', PerfilPessoa), ('ong', Ong)):
            with self.subTest(tipo=tipo), patch.object(modelo, 'save', side_effect=IntegrityError):
                resposta = self.enviar(tipo)
                self.assertEqual(resposta.status_code, 200)
                self.assertTrue(resposta.context['form_conta'].non_field_errors())
                self.assert_sem_cadastro()

    def test_falha_ao_salvar_ods_desfaz_ong_e_usuario(self):
        with patch('contas.forms.OngCadastroForm._save_m2m', side_effect=IntegrityError):
            self.enviar('ong')
        self.assert_sem_cadastro()

    def test_formularios_vazios_usam_localidades_do_banco(self):
        for tipo in ('pessoa', 'agricultor', 'ong'):
            with self.subTest(tipo=tipo):
                resposta = self.client.get(reverse('contas:cadastro_perfil', args=[tipo]))
                self.assertContains(resposta, str(self.localidade))
                self.assertNotContains(resposta, 'value="mariana.costa"')
                self.assertNotContains(resposta, 'simularCadastro')
                self.assertContains(resposta, 'name="csrfmiddlewaretoken"')
                self.assertEqual(list(resposta.context['form_perfil'].fields['localidade'].queryset), [self.localidade])

    def test_erros_preservam_dados_mas_nao_senha(self):
        resposta = self.enviar(password2='diferente')
        self.assertContains(resposta, 'value="Pessoa de teste"')
        self.assertNotContains(resposta, 'value="Senha-forte!82x"')

    def test_perfil_invalido_da_404(self):
        self.assertEqual(self.enviar('administrador').status_code, 404)
        self.assert_sem_cadastro()

    def test_autenticado_nao_cria_outra_conta(self):
        usuario = criar_doador().usuario
        self.client.force_login(usuario)
        resposta = self.enviar()
        self.assertRedirects(resposta, reverse('contas:minha_conta'), fetch_redirect_response=False)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(self.client.session['_auth_user_id'], str(usuario.pk))

    def test_cadastro_exige_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        resposta = cliente.post(reverse('contas:cadastro'), self.dados())
        self.assertEqual(resposta.status_code, 403)
        self.assert_sem_cadastro()

    @override_settings(DEBUG=True)
    def test_cadastro_remove_perfil_simulado_e_ignora_next_externo(self):
        sessao = self.client.session
        sessao[CHAVE_SESSAO_MOCK] = 'ong'
        sessao.save()
        resposta = self.enviar(next='https://outro.example/')
        self.assertRedirects(resposta, reverse('contas:minha_conta'), fetch_redirect_response=False)
        self.assertNotIn(CHAVE_SESSAO_MOCK, self.client.session)


class AutenticacaoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = criar_doador().usuario

    def entrar(self, **dados):
        return self.client.post(reverse('contas:entrar'), {
            'username': self.usuario.username, 'password': 'senha-de-teste-123', **dados})

    def test_login_autentica_e_menu_muda(self):
        resposta = self.client.get(reverse('core:inicio'))
        self.assertContains(resposta, '>Entrar</a>')
        self.assertContains(resposta, '>Cadastrar</a>')
        self.entrar()
        self.assertEqual(self.client.session['_auth_user_id'], str(self.usuario.pk))
        resposta = self.client.get(reverse('core:inicio'))
        self.assertContains(resposta, '>Minha conta</a>')
        self.assertContains(resposta, '>Sair</button>')
        self.assertNotContains(resposta, '>Entrar</a>')

    def test_login_rejeita_senha_errada_e_usuario_inativo(self):
        resposta = self.entrar(password='errada')
        self.assertTrue(resposta.context['form'].errors)
        self.usuario.is_active = False
        self.usuario.save()
        resposta = self.entrar()
        self.assertTrue(resposta.context['form'].errors)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_next_interno_e_preservado_e_aceito(self):
        destino = reverse('core:inicio')
        resposta = self.client.get(reverse('contas:entrar'), {'next': destino})
        self.assertContains(resposta, f'name="next" value="{destino}"')
        self.assertRedirects(self.entrar(next=destino), destino)

    def test_next_externo_e_rejeitado(self):
        for destino in ('https://outro.example/', '//outro.example/'):
            with self.subTest(destino=destino):
                self.assertRedirects(self.entrar(next=destino), reverse('contas:minha_conta'),
                                     fetch_redirect_response=False)

    def test_logout_exige_post_e_encerra_sessao(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('contas:sair')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.post(reverse('contas:sair')), reverse('core:inicio'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_e_logout_exigem_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(cliente.post(reverse('contas:entrar'), {}).status_code, 403)
        cliente.force_login(self.usuario)
        self.assertEqual(cliente.post(reverse('contas:sair')).status_code, 403)
        self.assertIn('_auth_user_id', cliente.session)

    def test_destino_minha_conta_respeita_cada_perfil(self):
        for perfil, destino in ((criar_doador(), 'contas:contribuicoes'),
                                (criar_agricultor(), 'colheita:minhas_ofertas'),
                                (criar_ong(situacao='pendente'), 'ongs:minha_ong')):
            with self.subTest(destino=destino):
                self.client.force_login(perfil.usuario)
                self.assertRedirects(self.client.get(reverse('contas:minha_conta')), reverse(destino),
                                     fetch_redirect_response=False)

    @override_settings(DEBUG=True)
    def test_login_limpa_mock_e_perfil_real_tem_precedencia(self):
        sessao = self.client.session
        sessao[CHAVE_SESSAO_MOCK] = 'agricultor'
        sessao.save()
        self.entrar()
        self.assertNotIn(CHAVE_SESSAO_MOCK, self.client.session)
        sessao = self.client.session
        sessao[CHAVE_SESSAO_MOCK] = 'ong'
        sessao.save()
        resposta = self.client.get(reverse('core:inicio'))
        self.assertEqual(resposta.context['perfil'], 'pessoa')
