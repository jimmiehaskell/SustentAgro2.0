"""BL-29: regras complementares e ações do admin. RF-10, RF-11, RN-14, RN-19, RN-20, E-05, P-11."""
from decimal import Decimal

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from colheita.models import Reserva
from colheita.services import saldo
from contas.models import Usuario
from core.perfis import perfil_da_requisicao
from core.tests.fabricas import criar_oferta, criar_ong
from ongs.services import aprovar_ong, reprovar_ong


class CnpjDaOngTest(TestCase):  # RF-10
    def test_cnpj_com_digito_errado_e_recusado(self):
        ong = criar_ong(cnpj='11222333000180')
        with self.assertRaises(ValidationError) as erro:
            ong.full_clean()
        self.assertIn('cnpj', erro.exception.message_dict)

    def test_cnpj_repetido_e_recusado(self):
        outra = criar_ong()
        ong = criar_ong(cnpj='11222333000181')
        ong.cnpj = outra.cnpj
        with self.assertRaises(ValidationError) as erro:
            ong.full_clean()
        self.assertIn('cnpj', erro.exception.message_dict)


class SituacaoComplementarTest(TestCase):
    def test_reprovar_sem_motivo_e_recusado(self):  # RN-20: a ONG precisa ver o motivo
        ong = criar_ong(situacao='pendente')
        with self.assertRaises(ValidationError):
            reprovar_ong(ong, '   ')
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'pendente')

    def test_aprovar_depois_de_reprovar_apaga_o_motivo(self):
        ong = criar_ong(situacao='pendente')
        reprovar_ong(ong, 'CNPJ de empresa com fins lucrativos.')
        aprovar_ong(ong)
        ong.refresh_from_db()
        self.assertEqual((ong.situacao, ong.motivo_reprovacao), ('ativa', ''))

    def test_ong_desativada_so_entra_na_minha_conta(self):  # RN-19, RN-20
        requisicao = RequestFactory().get('/')
        requisicao.user = criar_ong(situacao='desativada').usuario
        requisicao.session = {}
        self.assertEqual(perfil_da_requisicao(requisicao), 'ong-pendente')


class AcoesDoAdminTest(TestCase):  # RN-14, P-11: o administrador decide pelo admin do Django
    @classmethod
    def setUpTestData(cls):
        cls.administrador = Usuario.objects.create_superuser(username='administrador', password='senha-teste')

    def setUp(self):
        self.client.force_login(self.administrador)
        self.lista = reverse('admin:ongs_ong_changelist')

    def _acao(self, acao, ongs, **dados):
        return self.client.post(self.lista, {'action': acao, ACTION_CHECKBOX_NAME: [o.pk for o in ongs], **dados},
                                follow=True)

    def test_aprovar(self):  # RF-11
        ong = criar_ong(situacao='pendente')
        resposta = self._acao('aprovar', [ong])
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'ativa')
        self.assertIsNotNone(ong.aprovada_em)
        self.assertContains(resposta, '1 ONG(s) aprovada(s)')

    def test_reprovar_pede_o_motivo_antes(self):
        ong = criar_ong(situacao='pendente')
        resposta = self._acao('reprovar', [ong])
        self.assertContains(resposta, 'Motivo da reprovação')
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'pendente')

    def test_reprovar_sem_motivo_continua_na_pagina_do_motivo(self):
        ong = criar_ong(situacao='pendente')
        resposta = self._acao('reprovar', [ong], reprovar_com_motivo='Reprovar', motivo='')
        self.assertContains(resposta, 'Motivo da reprovação')
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'pendente')

    def test_reprovar_com_motivo(self):  # RN-20
        ong = criar_ong(situacao='pendente')
        self._acao('reprovar', [ong], reprovar_com_motivo='Reprovar', motivo='CNPJ de empresa.')
        ong.refresh_from_db()
        self.assertEqual((ong.situacao, ong.motivo_reprovacao), ('reprovada', 'CNPJ de empresa.'))

    def test_desativar_cancela_reservas_e_avisa(self):  # RN-19, E-05
        ong = criar_ong()
        oferta = criar_oferta(quantidade='100')
        Reserva.objects.create(oferta=oferta, ong=ong, quantidade=Decimal('40'))
        resposta = self._acao('desativar', [ong])
        ong.refresh_from_db()
        self.assertEqual(ong.situacao, 'desativada')
        self.assertEqual(saldo(oferta), 100)
        self.assertContains(resposta, '1 reserva(s) ativa(s) cancelada(s)')

    def test_situacao_nao_e_editada_no_formulario(self):  # só pelas ações, que chamam os serviços
        ong = criar_ong(situacao='pendente')
        resposta = self.client.get(reverse('admin:ongs_ong_change', args=[ong.pk]))
        self.assertNotContains(resposta, 'name="situacao"')
