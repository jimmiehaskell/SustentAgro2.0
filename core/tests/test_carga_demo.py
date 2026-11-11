"""BL-27 parte 3 (Pedro): o comando carregar_demo grava os dados no banco. RF-32, RN-24, E-10, E-11."""
from datetime import date
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from colheita.models import Oferta, Reserva
from contas.models import Localidade, PerfilPessoa, Usuario
from core.demo import dados
from core.demo.carga import carregar, data_do_recebimento
from ongs.models import Necessidade, Ods, Ong
from ongs.services import validar_cnpj
from painel.services import agrupar_kg_por_mes, calcular_fatia_por_ods

SENHA = 'senha-de-teste-123'


class CargaDemoTest(TestCase):
    def setUp(self):
        self.resumo = carregar(SENHA)

    def test_cria_conteudo_para_todas_as_telas(self):  # RF-32
        self.assertEqual(Localidade.objects.count(), len(dados.LOCALIDADES))
        self.assertEqual(Ods.objects.count(), 6)
        self.assertEqual(Ong.objects.filter(situacao='ativa').count(), 6)
        self.assertTrue(Ong.objects.filter(situacao='pendente').exists())
        self.assertTrue(Ong.objects.filter(situacao='reprovada').exists())
        self.assertEqual(PerfilPessoa.objects.filter(eh_agricultor=True).count(), len(dados.AGRICULTORES))
        self.assertEqual(Necessidade.objects.count(), 10)                                 # A-01
        self.assertEqual(Oferta.objects.count(), len(dados.OFERTAS_ABERTAS) + len(dados.HISTORICO))
        self.assertEqual(self.resumo['reservas'], Reserva.objects.count())

    def test_cnpjs_passam_na_validacao_do_cadastro(self):  # RN-24, E-11, RF-10
        for ong in Ong.objects.all():
            self.assertTrue(validar_cnpj(ong.cnpj), ong.nome)

    def test_rodar_de_novo_nao_duplica(self):
        carregar(SENHA)
        self.assertEqual(Ong.objects.count(), len(dados.ONGS))
        self.assertEqual(Localidade.objects.count(), len(dados.LOCALIDADES))
        self.assertEqual(Reserva.objects.count(), self.resumo['reservas'])

    def test_nao_apaga_superusuario(self):
        Usuario.objects.create_superuser('admin-teste', 'admin@exemplo.com', SENHA)
        carregar(SENHA)
        self.assertTrue(Usuario.objects.filter(username='admin-teste').exists())

    def test_contas_entram_com_a_senha(self):
        self.assertTrue(self.client.login(username='antonio.ribeiro', password=SENHA))
        self.assertTrue(self.client.login(username='solnascente', password=SENHA))

    def test_ofertas_abertas_nao_estao_vencidas(self):
        for oferta in Oferta.objects.filter(reservas__situacao='ativa').distinct():
            self.assertFalse(oferta.vencida, oferta.produto)

    def test_historico_alimenta_o_painel(self):  # RF-30, RF-31, E-10
        reservas = Reserva.objects.select_related('oferta', 'ong').prefetch_related('ong__ods')
        kg = [quilos for _, quilos in agrupar_kg_por_mes(reservas)]
        self.assertEqual(kg, [320, 540, 610, 880, 1130, 900])
        self.assertGreaterEqual(len(calcular_fatia_por_ods(reservas)), 4)

    def test_nenhum_recebimento_no_futuro(self):
        self.assertFalse(Reserva.objects.filter(recebida_em__gt=timezone.now()).exists())


class DataDoRecebimentoTest(TestCase):
    def test_volta_meses_atravessando_o_ano(self):
        self.assertEqual(data_do_recebimento(3, 15, date(2027, 2, 10)).date(), date(2026, 11, 15))

    def test_no_mes_atual_nao_passa_de_hoje(self):
        self.assertEqual(data_do_recebimento(0, 20, date(2026, 11, 5)).date(), date(2026, 11, 5))


class ComandoCarregarDemoTest(TestCase):
    def test_comando_com_noinput(self):
        saida = StringIO()
        call_command('carregar_demo', '--noinput', '--senha', SENHA, stdout=saida)
        self.assertIn('Dados de demonstração carregados', saida.getvalue())
        self.assertTrue(Ong.objects.exists())

    def test_sem_confirmar_nao_apaga_nada(self):
        from unittest.mock import patch
        with patch('builtins.input', return_value='não'):
            with self.assertRaises(CommandError):
                call_command('carregar_demo', '--senha', SENHA, stdout=StringIO())
        self.assertFalse(Ong.objects.exists())
