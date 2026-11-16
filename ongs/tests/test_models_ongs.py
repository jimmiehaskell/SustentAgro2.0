"""BL-25 (Júlia): contratos e validações dos models de ongs. RF-11, RF-12, RN-02, RN-21, RNF-06, A-01, A-04."""
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from contas.models import Usuario
from core.perfis import perfil_da_requisicao
from core.tests.fabricas import criar_localidade, criar_ods, criar_ong, criar_usuario
from ongs.models import Necessidade, Ods, Ong
from ongs.services import (TAMANHO_MAXIMO_DA_IMAGEM, criar_necessidade, editar_necessidade, encerrar_necessidade, validar_tamanho_da_imagem)

def _necessidade(ong, titulo='Cestas básicas', meta='60', **campos):
    return Necessidade.objects.create(ong=ong, titulo=titulo, tipo=campos.pop('tipo', 'itens'),
                                      unidade=campos.pop('unidade', 'cestas'), meta=Decimal(meta), **campos)


class OdsTest(TestCase):
    def test_numero_e_unico(self):
        criar_ods(2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Ods.objects.create(numero=2, nome='Repetido', cor='#000000')

    def test_ordenado_pelo_numero(self):
        for numero in (10, 1, 4):
            criar_ods(numero)
        self.assertEqual(list(Ods.objects.values_list('numero', flat=True)), [1, 4, 10])


class OngTest(TestCase):
    def test_ong_nova_nasce_pendente_e_sem_consulta_de_cnpj(self):  # RF-11
        ong = Ong.objects.create(usuario=criar_usuario('ong'), nome='ONG Nova', nome_curto='Nova',
                                 cnpj='11222333000181', telefone='(61) 3333-0000',
                                 email_contato='nova@exemplo.org', localidade=criar_localidade())
        self.assertEqual(ong.situacao, 'pendente')
        self.assertEqual(ong.verificacao_cnpj, 'nao_consultado')
        self.assertIsNotNone(ong.criada_em)
        self.assertIsNone(ong.aprovada_em)
        self.assertEqual(ong.familias_por_mes, 0)

    def test_nome_nome_curto_e_cnpj_sao_unicos(self):
        ong = criar_ong()
        for campo in ('nome', 'nome_curto', 'cnpj'):
            with self.subTest(campo=campo):
                outra = criar_ong()
                setattr(outra, campo, getattr(ong, campo))
                with self.assertRaises(IntegrityError), transaction.atomic():
                    outra.save()

    def test_conta_de_pessoa_nao_pode_ter_perfil_de_ong(self):  # ADR-002
        ong = criar_ong()
        ong.usuario = criar_usuario('pessoa')
        with self.assertRaises(ValidationError) as erro:
            ong.full_clean()
        self.assertIn('usuario', erro.exception.message_dict)

    def test_ong_valida_passa_no_full_clean(self):
        criar_ong().full_clean()

    def test_ods_e_localidade_acessam_as_ongs(self):
        ong = criar_ong(localidade='Gama', ods=(1, 2))
        self.assertEqual(list(ong.ods.values_list('numero', flat=True)), [1, 2])
        self.assertQuerySetEqual(criar_ods(2).ongs.all(), [ong])
        self.assertQuerySetEqual(criar_localidade('Gama').ongs.all(), [ong])

    def test_localidade_em_uso_nao_pode_ser_excluida(self):
        ong = criar_ong()
        with self.assertRaises(ProtectedError):
            ong.localidade.delete()

    def test_excluir_usuario_exclui_a_ong_e_as_necessidades(self):
        ong = criar_ong()
        _necessidade(ong)
        ong.usuario.delete()
        self.assertFalse(Ong.objects.filter(pk=ong.pk).exists())
        self.assertFalse(Necessidade.objects.exists())


class ImagemDaOngTest(TestCase):  # RNF-06
    def test_recusa_formato_fora_da_lista(self):
        ong = criar_ong()
        ong.logo = SimpleUploadedFile('logo.gif', b'GIF89a', content_type='image/gif')
        with self.assertRaises(ValidationError) as erro:
            ong.full_clean()
        self.assertIn('logo', erro.exception.message_dict)

    def test_aceita_os_formatos_da_lista(self):
        ong = criar_ong()
        for nome in ('capa.jpeg', 'capa.jpg', 'capa.png', 'capa.webp'):
            with self.subTest(nome=nome):
                ong.capa = SimpleUploadedFile(nome, b'imagem')
                ong.full_clean()

    def test_limite_de_10_mb(self):
        validar_tamanho_da_imagem(SimpleNamespace(size=TAMANHO_MAXIMO_DA_IMAGEM))
        with self.assertRaises(ValidationError):
            validar_tamanho_da_imagem(SimpleNamespace(size=TAMANHO_MAXIMO_DA_IMAGEM + 1))


class NecessidadeTest(TestCase):
    def test_mais_recente_primeiro(self):  # RF-05: "Precisa agora" pega a primeira aberta
        ong = criar_ong()
        antiga = _necessidade(ong, 'Gás de cozinha')
        nova = _necessidade(ong, 'Cestas básicas')
        Necessidade.objects.filter(pk=antiga.pk).update(criada_em=timezone.now() - timedelta(days=1))
        self.assertEqual(list(ong.necessidades.all()), [nova, antiga])

    def test_nasce_aberta(self):
        self.assertEqual(_necessidade(criar_ong()).situacao, 'aberta')

    def test_barra_comeca_em_zero_sem_contribuicoes(self):  # RN-02, A-01
        necessidade = _necessidade(criar_ong())
        self.assertEqual(necessidade.confirmado, Decimal('0'))
        self.assertEqual(necessidade.percentual, 0)

    def test_atendida_fica_com_a_barra_cheia(self):  # RN-21
        self.assertEqual(_necessidade(criar_ong(), situacao='atendida').percentual, 100)

    def test_meta_precisa_ser_positiva(self):
        necessidade = _necessidade(criar_ong(), meta='0')
        with self.assertRaises(ValidationError) as erro:
            necessidade.full_clean()
        self.assertIn('meta', erro.exception.message_dict)

    def test_tipo_usa_os_mesmos_valores_do_tipo_de_ajuda(self):  # A-04
        necessidade = _necessidade(criar_ong(), tipo='voluntarios')
        with self.assertRaises(ValidationError) as erro:
            necessidade.full_clean()
        self.assertIn('tipo', erro.exception.message_dict)


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

class PerfilDaContaDeOngTest(TestCase):  # RN-20: o perfil vem da situação da Ong
    def _perfil(self, usuario):
        requisicao = RequestFactory().get('/')
        requisicao.user = usuario
        requisicao.session = {}
        return perfil_da_requisicao(requisicao)

    def test_perfil_segue_a_situacao_da_ong(self):
        for situacao, perfil in (('ativa', 'ong'), ('pendente', 'ong-pendente'), ('reprovada', 'ong-reprovada')):
            with self.subTest(situacao=situacao):
                self.assertEqual(self._perfil(criar_ong(situacao=situacao).usuario), perfil)

    def test_conta_de_ong_sem_perfil_conta_como_pendente(self):
        self.assertEqual(self._perfil(criar_usuario('ong')), 'ong-pendente')


class AdminOngsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = Usuario.objects.create_superuser(username='administrador', password='senha-teste')
        cls.ong = criar_ong()
        _necessidade(cls.ong)

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_listas_do_admin_abrem(self):
        for nome in ('ongs_ods_changelist', 'ongs_ong_changelist', 'ongs_necessidade_changelist'):
            with self.subTest(nome=nome):
                self.assertEqual(self.client.get(reverse(f'admin:{nome}')).status_code, 200)

    def test_ong_abre_com_as_necessidades(self):
        resposta = self.client.get(reverse('admin:ongs_ong_change', args=[self.ong.pk]))
        self.assertContains(resposta, 'Cestas básicas')
