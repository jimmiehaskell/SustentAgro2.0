"""BL-47 (Gabriel): cancelar reserva e oferta. RF-24, RN-03, RN-18, UC-09, UC-11, RNF-05."""
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from colheita.services import (cancelar_oferta, cancelar_reserva, confirmar_recebimento, ofertas_da_lista,
                               reservar_oferta, saldo)
from core.tests import fabricas


class CancelarReservaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg')
        self.reserva = reservar_oferta(self.oferta, self.ong, Decimal('40'))

    def test_cancela_grava_quem_cancelou_e_devolve_o_saldo(self):  # RF-24
        self.assertEqual(saldo(self.oferta), Decimal('60'))
        for quem in ('ong', 'agricultor'):
            with self.subTest(quem=quem):
                reserva = reservar_oferta(self.oferta, self.ong, Decimal('10'))
                reserva = cancelar_reserva(reserva, quem)
                self.assertEqual((reserva.situacao, reserva.cancelada_por), ('cancelada', quem))
                reserva.refresh_from_db()
                self.assertEqual((reserva.situacao, reserva.cancelada_por), ('cancelada', quem))
        self.assertEqual(saldo(self.oferta), Decimal('60'))
        cancelar_reserva(self.reserva, 'ong')
        self.assertEqual(saldo(self.oferta), Decimal('100'))

    def test_reserva_encerrada_nao_cancela(self):
        recebida = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(recebida, Decimal('10'))
        nao_recebida = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(nao_recebida, Decimal('0'))
        cancelada = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        cancelar_reserva(cancelada, 'ong')
        for reserva, situacao in ((recebida, 'recebida'), (nao_recebida, 'nao_recebida'), (cancelada, 'cancelada')):
            with self.subTest(situacao=situacao):
                with self.assertRaisesMessage(ValidationError, 'Só uma reserva ativa pode ser cancelada.'):
                    cancelar_reserva(reserva, 'agricultor')
                reserva.refresh_from_db()
                self.assertEqual(reserva.situacao, situacao)
        self.assertEqual(cancelada.cancelada_por, 'ong')

    def test_recebida_continua_contando_no_saldo(self):  # RN-03
        recebida = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(recebida, Decimal('10'))
        with self.assertRaises(ValidationError):
            cancelar_reserva(recebida, 'ong')
        self.assertEqual(saldo(self.oferta), Decimal('50'))

    def test_oferta_vencida_ainda_cancela_a_reserva(self):  # RN-18, E-04
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        self.assertEqual(cancelar_reserva(self.reserva, 'ong').situacao, 'cancelada')


class CancelarOfertaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg')

    def test_sem_reservas_cancela_e_sai_da_lista(self):  # RF-24
        self.assertEqual(ofertas_da_lista(), [self.oferta])
        self.assertEqual(cancelar_oferta(self.oferta).situacao, 'cancelada')
        self.oferta.refresh_from_db()
        self.assertEqual(self.oferta.situacao, 'cancelada')
        self.assertEqual(ofertas_da_lista(), [])

    def test_reserva_ativa_impede_o_cancelamento(self):  # RF-24
        reserva = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        with self.assertRaisesMessage(ValidationError, 'Só é possível cancelar ofertas sem reservas ativas.'):
            cancelar_oferta(self.oferta)
        self.oferta.refresh_from_db()
        self.assertEqual(self.oferta.situacao, 'aberta')
        cancelar_reserva(reserva, 'agricultor')
        self.assertEqual(cancelar_oferta(self.oferta).situacao, 'cancelada')

    def test_reservas_encerradas_nao_impedem(self):
        recebida = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(recebida, Decimal('10'))
        nao_recebida = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        confirmar_recebimento(nao_recebida, Decimal('0'))
        self.assertEqual(cancelar_oferta(self.oferta).situacao, 'cancelada')

    def test_oferta_ja_cancelada_nao_cancela_de_novo(self):
        cancelar_oferta(self.oferta)
        with self.assertRaisesMessage(ValidationError, 'Esta oferta já foi cancelada.'):
            cancelar_oferta(self.oferta)

    def test_oferta_cancelada_nao_recebe_reserva(self):
        cancelar_oferta(self.oferta)
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, self.ong, Decimal('10'))


class CancelarReservaDaOngNaTelaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg', produto='Alface crespa')
        self.reserva = reservar_oferta(self.oferta, self.ong, Decimal('50'))
        self.url = reverse('colheita:cancelar_reserva', kwargs={'pk': self.reserva.pk})
        self.client.force_login(self.ong.usuario)

    def textos(self, resposta):
        return [str(m) for m in resposta.context['messages']]

    def test_cancela_grava_ong_e_o_saldo_volta_para_a_lista(self):  # RF-24
        self.assertContains(self.client.get(reverse('colheita:ofertas')), 'Saldo <strong class="text-numero">50 kg</strong>')
        resposta = self.client.post(self.url, follow=True)
        self.assertRedirects(resposta, reverse('colheita:minhas_reservas'))
        self.assertEqual(self.textos(resposta), ['Reserva de Alface crespa cancelada. '
                                                 'A quantidade voltou ao saldo da oferta.'])
        self.reserva.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.reserva.cancelada_por), ('cancelada', 'ong'))
        self.assertEqual(resposta.context['ativas'], [])
        self.assertEqual(resposta.context['recebidas'], [])
        self.assertContains(self.client.get(reverse('colheita:ofertas')), 'Saldo <strong class="text-numero">100 kg</strong>')

    def test_oferta_vencida_nao_promete_saldo(self):  # RN-18
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        resposta = self.client.post(self.url, follow=True)
        self.assertEqual(self.textos(resposta), ['Reserva de Alface crespa cancelada.'])

    def test_reserva_ja_encerrada_mostra_erro_e_nao_muda(self):
        confirmar_recebimento(self.reserva, Decimal('40'))
        resposta = self.client.post(self.url, follow=True)
        self.assertEqual(self.textos(resposta), ['Só uma reserva ativa pode ser cancelada.'])
        self.reserva.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.reserva.cancelada_por), ('recebida', ''))

    def test_reserva_de_outra_ong_ou_inexistente_da_404(self):  # RNF-05
        reserva_da_outra = reservar_oferta(self.oferta, fabricas.criar_ong(), Decimal('10'))
        for pk in (reserva_da_outra.pk, 99999):
            with self.subTest(pk=pk):
                url = reverse('colheita:cancelar_reserva', kwargs={'pk': pk})
                self.assertEqual(self.client.post(url).status_code, 404)
        reserva_da_outra.refresh_from_db()
        self.assertEqual(reserva_da_outra.situacao, 'ativa')

    def test_visitante_vai_para_o_login(self):
        self.client.logout()
        self.assertRedirects(self.client.post(self.url), f"{reverse('contas:entrar')}?next={self.url}")
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_ong_inativa_agricultor_e_doador_recebem_403(self):
        usuarios = [fabricas.criar_ong(situacao='pendente').usuario, fabricas.criar_ong(situacao='desativada').usuario,
                    fabricas.criar_agricultor().usuario, fabricas.criar_doador().usuario]
        for usuario in usuarios:
            with self.subTest(usuario=usuario):
                self.client.force_login(usuario)
                self.assertEqual(self.client.post(self.url).status_code, 403)
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'ativa')

    def test_get_nao_e_aceito(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_botao_do_cartao_aponta_para_o_cancelamento(self):
        resposta = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertContains(resposta, f'formaction="{self.url}"')

    def test_botao_pede_confirmacao_antes_de_cancelar(self):
        resposta = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertContains(resposta, "return confirm('Cancelar a reserva de")


class CancelarComoAgricultorNaTelaTest(TestCase):
    def setUp(self):
        self.agricultor = fabricas.criar_agricultor()
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(agricultor=self.agricultor, quantidade='100', unidade='kg',
                                            produto='Alface crespa')
        self.reserva = reservar_oferta(self.oferta, self.ong, Decimal('50'))
        self.url_reserva = reverse('colheita:cancelar_reserva_do_agricultor', kwargs={'pk': self.reserva.pk})
        self.url_oferta = reverse('colheita:cancelar_oferta', kwargs={'pk': self.oferta.pk})
        self.client.force_login(self.agricultor.usuario)

    def textos(self, resposta):
        return [str(m) for m in resposta.context['messages']]

    def test_agricultor_cancela_a_reserva_e_o_saldo_volta(self):  # RF-24, UC-11
        resposta = self.client.post(self.url_reserva, follow=True)
        self.assertRedirects(resposta, reverse('colheita:minhas_ofertas'))
        self.assertEqual(self.textos(resposta), ['Reserva de Alface crespa cancelada. '
                                                 'A quantidade voltou ao saldo da oferta.'])
        self.reserva.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.reserva.cancelada_por), ('cancelada', 'agricultor'))
        self.assertEqual(saldo(self.oferta), Decimal('100'))

    def test_reserva_encerrada_mostra_erro_e_nao_muda(self):
        confirmar_recebimento(self.reserva, Decimal('0'))
        resposta = self.client.post(self.url_reserva, follow=True)
        self.assertEqual(self.textos(resposta), ['Só uma reserva ativa pode ser cancelada.'])
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.situacao, 'nao_recebida')

    def test_oferta_com_reserva_ativa_nao_cancela(self):  # RF-24
        resposta = self.client.post(self.url_oferta, follow=True)
        self.assertEqual(self.textos(resposta), ['Só é possível cancelar ofertas sem reservas ativas. '
                                                 'Cancele as reservas primeiro.'])
        self.oferta.refresh_from_db()
        self.assertEqual(self.oferta.situacao, 'aberta')

    def test_oferta_sem_reserva_ativa_cancela_e_sai_da_lista(self):  # RF-24
        self.client.post(self.url_reserva, follow=True)
        self.assertEqual([o.pk for o in ofertas_da_lista()], [self.oferta.pk])
        resposta = self.client.post(self.url_oferta, follow=True)
        self.assertRedirects(resposta, reverse('colheita:minhas_ofertas'))
        self.assertEqual(self.textos(resposta), ['Oferta de Alface crespa cancelada. Ela saiu da lista das ONGs.'])
        self.oferta.refresh_from_db()
        self.assertEqual(self.oferta.situacao, 'cancelada')
        self.assertEqual(ofertas_da_lista(), [])
        self.assertNotContains(self.client.get(reverse('colheita:ofertas')), 'Alface crespa')

    def test_oferta_ja_cancelada_mostra_erro(self):
        self.client.post(self.url_reserva, follow=True)
        self.client.post(self.url_oferta, follow=True)
        resposta = self.client.post(self.url_oferta, follow=True)
        self.assertEqual(self.textos(resposta), ['Esta oferta já foi cancelada.'])

    def test_dado_de_outro_agricultor_ou_inexistente_da_404(self):  # RNF-05
        self.client.force_login(fabricas.criar_agricultor().usuario)
        for url in (self.url_reserva, self.url_oferta,
                    reverse('colheita:cancelar_reserva_do_agricultor', kwargs={'pk': 99999}),
                    reverse('colheita:cancelar_oferta', kwargs={'pk': 99999})):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 404)
        self.reserva.refresh_from_db()
        self.oferta.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.oferta.situacao), ('ativa', 'aberta'))

    def test_visitante_vai_para_o_login(self):
        self.client.logout()
        for url in (self.url_reserva, self.url_oferta):
            with self.subTest(url=url):
                self.assertRedirects(self.client.post(url), f"{reverse('contas:entrar')}?next={url}")

    def test_ong_e_doador_recebem_403(self):
        for usuario in (self.ong.usuario, fabricas.criar_doador().usuario):
            self.client.force_login(usuario)
            for url in (self.url_reserva, self.url_oferta):
                with self.subTest(usuario=usuario, url=url):
                    self.assertEqual(self.client.post(url).status_code, 403)
        self.reserva.refresh_from_db()
        self.oferta.refresh_from_db()
        self.assertEqual((self.reserva.situacao, self.oferta.situacao), ('ativa', 'aberta'))

    def test_get_nao_e_aceito(self):
        for url in (self.url_reserva, self.url_oferta):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 405)
