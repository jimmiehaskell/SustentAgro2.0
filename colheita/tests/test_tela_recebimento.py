"""BL-35 (Gabriel): confirmar recebimento na Tela 11. RF-23, RN-16, RN-17, RN-18, E-02, E-03."""
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from colheita.services import confirmar_recebimento, reservar_oferta, saldo
from core.tests import fabricas


class RegrasDoRecebimentoTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg')
        self.reserva = reservar_oferta(self.oferta, self.ong, Decimal('50'))

    def test_recebido_zero_nao_grava_data_e_fica_com_quantidade_zero(self):  # RN-17
        reserva = confirmar_recebimento(self.reserva, Decimal('0'))
        self.assertEqual(reserva.quantidade_recebida, Decimal('0'))
        self.assertIsNone(reserva.recebida_em)

    def test_valor_negativo_e_recusado(self):  # RN-17
        with self.assertRaises(ValidationError):
            confirmar_recebimento(self.reserva, Decimal('-1'))

    def test_mensagem_de_excesso_traz_o_reservado(self):  # E-02
        with self.assertRaisesMessage(ValidationError, 'A quantidade recebida vai de 0 até 50 kg.'):
            confirmar_recebimento(self.reserva, Decimal('50.1'))

    def test_recusado_nao_muda_a_reserva(self):  # E-02
        with self.assertRaises(ValidationError):
            confirmar_recebimento(self.reserva, Decimal('60'))
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')
        self.assertIsNone(self.reserva.quantidade_recebida)

    def test_kg_recusa_duas_casas_decimais(self):  # RN-16
        with self.assertRaises(ValidationError):
            confirmar_recebimento(self.reserva, Decimal('10.25'))
        self.assertEqual(confirmar_recebimento(self.reserva, Decimal('10.5')).quantidade_recebida, Decimal('10.5'))

    def test_un_recusa_fracao(self):  # RN-16
        oferta = fabricas.criar_oferta(quantidade='40', unidade='un')
        reserva = reservar_oferta(oferta, self.ong, Decimal('20'))
        with self.assertRaisesMessage(ValidationError, 'Em unidades, informe só números inteiros.'):
            confirmar_recebimento(reserva, Decimal('2.5'))

    def test_reserva_ja_encerrada_nao_confirma_de_novo(self):
        confirmar_recebimento(self.reserva, Decimal('50'))
        with self.assertRaisesMessage(ValidationError, 'Esta reserva já foi encerrada.'):
            confirmar_recebimento(self.reserva, Decimal('10'))
        zerada = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(zerada, Decimal('0'))
        with self.assertRaises(ValidationError):
            confirmar_recebimento(zerada, Decimal('10'))

    def test_oferta_vencida_aceita_zero_e_a_reserva_encerra(self):  # RN-18, E-04, E-03
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        self.assertEqual(confirmar_recebimento(self.reserva, Decimal('0')).situacao, 'nao_recebida')


class ConfirmarNaTelaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg', produto='Alface crespa')
        self.reserva = reservar_oferta(self.oferta, self.ong, Decimal('50'))
        self.url = reverse('colheita:confirmar_recebimento', kwargs={'pk': self.reserva.pk})
        self.client.force_login(self.ong.usuario)

    def confirmar(self, quantidade, url=None):
        return self.client.post(url or self.url, {'quantidade_recebida': quantidade}, follow=True)

    def textos(self, resposta):
        return [str(m) for m in resposta.context['messages']]

    def test_recebimento_parcial_passa_para_recebidas(self):  # RF-23
        resposta = self.confirmar('48')
        self.assertRedirects(resposta, reverse('colheita:minhas_reservas'))
        self.assertEqual(self.textos(resposta), ['Recebimento confirmado: 48 kg de Alface crespa. '
                                                 'A quantidade já conta no painel de impacto.'])
        self.reserva.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.reserva.quantidade_recebida), ('recebida', Decimal('48')))
        self.assertIsNotNone(self.reserva.recebida_em)
        self.assertEqual(resposta.context['ativas'], [])
        self.assertEqual(resposta.context['recebidas'], [self.reserva])
        self.assertContains(resposta, 'Contou 48 kg no painel de impacto')

    def test_virgula_decimal_e_aceita(self):  # RN-16
        self.confirmar('12,5')
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.quantidade_recebida, Decimal('12.5'))

    def test_zero_encerra_e_a_quantidade_volta_para_a_lista(self):  # RN-17, E-03
        self.assertContains(self.client.get(reverse('colheita:ofertas')), 'Saldo <strong class="text-numero">50 kg</strong>')
        resposta = self.confirmar('0')
        self.assertEqual(self.textos(resposta), ['Reserva de Alface crespa encerrada como não recebida. '
                                                 'A quantidade voltou ao saldo da oferta.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'nao_recebida')
        self.assertEqual(saldo(self.oferta), Decimal('100'))
        self.assertEqual(resposta.context['recebidas'], [])
        self.assertContains(self.client.get(reverse('colheita:ofertas')), 'Saldo <strong class="text-numero">100 kg</strong>')

    def test_zero_em_oferta_vencida_nao_promete_saldo(self):  # RN-18
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        resposta = self.confirmar('0')
        self.assertEqual(self.textos(resposta), ['Reserva de Alface crespa encerrada como não recebida.'])

    def test_oferta_vencida_ainda_confirma_pela_tela(self):  # RN-18, E-04
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        resposta = self.confirmar('50')
        self.assertEqual(resposta.context['recebidas'], [self.reserva])

    def test_acima_do_reservado_mostra_o_erro_e_nao_muda(self):  # E-02
        resposta = self.confirmar('51')
        self.assertEqual(self.textos(resposta), ['A quantidade recebida vai de 0 até 50 kg.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_fracao_invalida_nao_confirma(self):  # RN-16
        resposta = self.confirmar('10.25')
        self.assertEqual(self.textos(resposta), ['Em kg, informe no máximo uma casa decimal.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_texto_ou_vazio_nao_confirma(self):
        for valor in ('abc', '', 'NaN', 'Infinity', '-Infinity'):
            with self.subTest(valor=valor):
                self.assertEqual(self.textos(self.confirmar(valor)), ['Informe a quantidade recebida em números.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_negativo_nao_confirma(self):  # RN-17
        self.assertEqual(self.textos(self.confirmar('-5')), ['A quantidade recebida vai de 0 até 50 kg.'])

    def test_reserva_ja_recebida_mostra_erro_e_nao_muda(self):
        self.confirmar('40')
        resposta = self.confirmar('10')
        self.assertEqual(self.textos(resposta), ['Esta reserva já foi encerrada.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.quantidade_recebida, Decimal('40'))

    def test_reserva_de_outra_ong_ou_inexistente_da_404(self):
        outra = fabricas.criar_ong()
        reserva_da_outra = reservar_oferta(self.oferta, outra, Decimal('10'))
        for pk in (reserva_da_outra.pk, 99999):
            with self.subTest(pk=pk):
                url = reverse('colheita:confirmar_recebimento', kwargs={'pk': pk})
                self.assertEqual(self.client.post(url, {'quantidade_recebida': '5'}).status_code, 404)
        reserva_da_outra.refresh_from_db()
        self.assertEqual(reserva_da_outra.situacao, 'ativa')

    def test_visitante_vai_para_o_login(self):
        self.client.logout()
        resposta = self.client.post(self.url, {'quantidade_recebida': '10'})
        self.assertRedirects(resposta, f"{reverse('contas:entrar')}?next={self.url}")
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_ong_inativa_agricultor_e_doador_recebem_403(self):
        usuarios = [fabricas.criar_ong(situacao='pendente').usuario, fabricas.criar_ong(situacao='desativada').usuario,
                    fabricas.criar_agricultor().usuario, fabricas.criar_doador().usuario]
        for usuario in usuarios:
            with self.subTest(usuario=usuario):
                self.client.force_login(usuario)
                self.assertEqual(self.client.post(self.url, {'quantidade_recebida': '10'}).status_code, 403)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_get_nao_e_aceito(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_formulario_do_cartao_aponta_para_a_confirmacao(self):
        resposta = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertContains(resposta, f'action="{self.url}"')
        self.assertContains(resposta, 'csrfmiddlewaretoken')
