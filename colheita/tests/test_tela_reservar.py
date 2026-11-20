"""BL-34 (Gabriel): reservar oferta e contato após a reserva. RF-20, RF-27, RN-01, RN-03, RN-16, E-01, E-04."""
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from colheita.choices import SituacaoOferta
from colheita.models import Reserva
from colheita.services import distancia_km, reservar_oferta, reservas_da_ong, saldo
from core.tests import fabricas


class RegrasDaReservaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg')

    def test_ong_desativada_e_reprovada_nao_reservam(self):  # RN-01
        for situacao in ('desativada', 'reprovada'):
            with self.subTest(situacao=situacao), self.assertRaises(ValidationError):
                reservar_oferta(self.oferta, fabricas.criar_ong(situacao=situacao), Decimal('10'))
        self.assertEqual(saldo(self.oferta), Decimal('100'))

    def test_kg_recusa_duas_casas_decimais(self):  # RN-16, E-01
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, self.ong, Decimal('1.25'))

    def test_quantidade_enorme_e_recusada_pelo_saldo(self):
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, self.ong, Decimal('1E+50'))

    def test_mensagem_de_saldo_traz_o_que_resta(self):  # RN-03
        reservar_oferta(self.oferta, self.ong, Decimal('80.5'))
        with self.assertRaisesMessage(ValidationError, 'Só restam 19,5 kg desta oferta.'):
            reservar_oferta(self.oferta, fabricas.criar_ong(), Decimal('30'))

    def test_reserva_de_todo_o_saldo_zera_a_oferta(self):  # RF-20
        reservar_oferta(self.oferta, self.ong, Decimal('100'))
        self.assertEqual(saldo(self.oferta), 0)
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, fabricas.criar_ong(), Decimal('0.1'))

    def test_oferta_vencida_nao_recebe_reserva_e_as_antigas_continuam(self):  # E-04, RN-18
        reserva = reservar_oferta(self.oferta, self.ong, Decimal('10'))
        self.oferta.colher_ate = date.today() - timedelta(days=1)
        self.oferta.save()
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, fabricas.criar_ong(), Decimal('10'))
        reserva.refresh_from_db()
        self.assertEqual(reserva.situacao, 'ativa')

    def test_oferta_cancelada_nao_recebe_reserva(self):
        self.oferta.situacao = SituacaoOferta.CANCELADA
        self.oferta.save()
        with self.assertRaises(ValidationError):
            reservar_oferta(self.oferta, self.ong, Decimal('10'))

    def test_duas_reservas_da_mesma_ong_somam(self):
        reservar_oferta(self.oferta, self.ong, Decimal('10'))
        reservar_oferta(self.oferta, self.ong, Decimal('15'))
        self.assertEqual(saldo(self.oferta), Decimal('75'))


class ReservarNaTelaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.oferta = fabricas.criar_oferta(quantidade='100', unidade='kg', produto='Alface crespa')
        self.url = reverse('colheita:reservar', kwargs={'pk': self.oferta.pk})
        self.client.force_login(self.ong.usuario)

    def reservar(self, quantidade, url=None):
        return self.client.post(url or self.url, {'quantidade': quantidade}, follow=True)

    def textos(self, resposta):
        return [str(m) for m in resposta.context['messages']]

    def test_ong_ativa_reserva_e_o_saldo_diminui(self):  # RF-20
        resposta = self.reservar('30')
        self.assertRedirects(resposta, reverse('colheita:ofertas'))
        self.assertEqual(self.textos(resposta), ['Reserva feita: 30 kg de Alface crespa. '
                                                 'O contato do agricultor está em Minhas reservas.'])
        self.assertEqual(saldo(self.oferta), Decimal('70'))
        self.assertEqual(Reserva.objects.get().ong, self.ong)
        self.assertContains(resposta, 'Saldo <strong class="text-numero">70 kg</strong>')

    def test_virgula_decimal_e_aceita(self):  # RN-16
        self.reservar('12,5')
        self.assertEqual(saldo(self.oferta), Decimal('87.5'))

    def test_acima_do_saldo_mostra_o_erro_e_nao_reserva(self):  # RN-03
        self.reservar('80')
        resposta = self.reservar('30')
        self.assertEqual(self.textos(resposta), ['Só restam 20 kg desta oferta.'])
        self.assertEqual(Reserva.objects.count(), 1)

    def test_texto_ou_vazio_nao_reserva(self):
        for valor in ('abc', '', 'NaN', 'Infinity'):
            with self.subTest(valor=valor):
                resposta = self.reservar(valor)
                self.assertEqual(self.textos(resposta), ['Informe a quantidade em números.'])
        self.assertEqual(Reserva.objects.count(), 0)

    def test_oferta_em_unidade_recusa_fracao(self):  # RN-16, E-01
        oferta = fabricas.criar_oferta(quantidade='40', unidade='un')
        resposta = self.reservar('2.5', reverse('colheita:reservar', kwargs={'pk': oferta.pk}))
        self.assertEqual(self.textos(resposta), ['Em unidades, informe só números inteiros.'])

    def test_reservar_todo_o_saldo_tira_a_oferta_da_lista(self):  # RF-20
        resposta = self.reservar('100')
        self.assertNotContains(resposta, 'Alface crespa</h3>')
        self.assertEqual(self.client.post(self.url, {'quantidade': '1'}).status_code, 404)

    def test_oferta_inexistente_vencida_ou_direcionada_a_outra_da_404(self):
        vencida = fabricas.criar_oferta(colher_ate=date.today() - timedelta(days=1))
        direcionada = fabricas.criar_oferta(ong_destino=fabricas.criar_ong())
        for pk in (99999, vencida.pk, direcionada.pk):
            with self.subTest(pk=pk):
                url = reverse('colheita:reservar', kwargs={'pk': pk})
                self.assertEqual(self.client.post(url, {'quantidade': '1'}).status_code, 404)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_oferta_direcionada_a_ong_pode_ser_reservada_por_ela(self):  # RN-04
        oferta = fabricas.criar_oferta(ong_destino=self.ong)
        self.reservar('5', reverse('colheita:reservar', kwargs={'pk': oferta.pk}))
        self.assertEqual(saldo(oferta), Decimal('95'))

    def test_visitante_vai_para_o_login(self):
        self.client.logout()
        resposta = self.client.post(self.url, {'quantidade': '10'})
        self.assertRedirects(resposta, f"{reverse('contas:entrar')}?next={self.url}")
        self.assertEqual(Reserva.objects.count(), 0)

    def test_ong_pendente_agricultor_e_doador_recebem_403(self):  # RN-01
        usuarios = [fabricas.criar_ong(situacao='pendente').usuario, fabricas.criar_ong(situacao='desativada').usuario,
                    fabricas.criar_agricultor().usuario, fabricas.criar_doador().usuario]
        for usuario in usuarios:
            with self.subTest(usuario=usuario):
                self.client.force_login(usuario)
                self.assertEqual(self.client.post(self.url, {'quantidade': '10'}).status_code, 403)
        self.assertEqual(Reserva.objects.count(), 0)

    def test_get_nao_e_aceito(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_formulario_do_cartao_aponta_para_a_reserva(self):
        resposta = self.client.get(reverse('colheita:ofertas'))
        self.assertContains(resposta, f'action="{self.url}"')
        self.assertContains(resposta, 'csrfmiddlewaretoken')

    def test_visitante_nao_ve_formulario_de_reserva(self):  # RF-28
        self.client.logout()
        self.assertNotContains(self.client.get(reverse('colheita:ofertas')), self.url)

    def test_mensagem_de_sucesso_usa_virgula(self):  # pt-BR
        resposta = self.reservar('12,5')
        self.assertEqual(self.textos(resposta), [
            'Reserva feita: 12,5 kg de Alface crespa. '
            'O contato do agricultor está em Minhas reservas.'
        ])


class ContatoAposReservaTest(TestCase):
    def setUp(self):
        self.ong = fabricas.criar_ong()
        self.agricultor = fabricas.criar_agricultor(nome_completo='Antônio Ribeiro')
        self.agricultor.usuario.email = 'antonio@exemplo.org'
        self.agricultor.usuario.save()
        self.oferta = fabricas.criar_oferta(agricultor=self.agricultor, quantidade='100', produto='Alface crespa')
        self.client.force_login(self.ong.usuario)

    def test_contato_nao_aparece_na_lista_so_depois_da_reserva(self):  # RF-27
        lista = self.client.get(reverse('colheita:ofertas'))
        self.assertNotContains(lista, '(61) 98123-4567')
        self.assertNotContains(lista, 'antonio@exemplo.org')
        self.assertContains(self.client.get(reverse('colheita:minhas_reservas')), 'Nenhuma reserva aguardando retirada')
        reservar_oferta(self.oferta, self.ong, Decimal('15'))
        reservas = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertContains(reservas, 'Alface crespa')
        self.assertContains(reservas, 'Antônio Ribeiro')
        self.assertContains(reservas, '(61) 98123-4567')
        self.assertContains(reservas, 'antonio@exemplo.org')

    def test_outra_ong_nao_ve_a_reserva_nem_o_contato(self):  # RF-27
        reservar_oferta(self.oferta, self.ong, Decimal('15'))
        self.client.force_login(fabricas.criar_ong().usuario)
        reservas = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertNotContains(reservas, '(61) 98123-4567')
        self.assertNotContains(reservas, 'antonio@exemplo.org')

    def test_minhas_reservas_separa_ativas_e_recebidas_com_distancia(self):
        ativa = reservar_oferta(self.oferta, self.ong, Decimal('15'))
        recebida = reservar_oferta(self.oferta, self.ong, Decimal('5'))
        recebida.situacao, recebida.quantidade_recebida = 'recebida', Decimal('5')
        recebida.save()
        resposta = self.client.get(reverse('colheita:minhas_reservas'))
        self.assertEqual(resposta.context['ativas'], [ativa])
        self.assertEqual(resposta.context['recebidas'], [recebida])
        self.assertEqual(reservas_da_ong(self.ong)[0].oferta.distancia_km,
                         distancia_km(self.ong.localidade, self.oferta.localidade))

    def test_minhas_reservas_so_para_ong_ativa(self):
        url = reverse('colheita:minhas_reservas')
        self.client.logout()
        self.assertRedirects(self.client.get(url), f"{reverse('contas:entrar')}?next={url}")
        self.client.force_login(fabricas.criar_ong(situacao='pendente').usuario)
        self.assertEqual(self.client.get(url).status_code, 403)
