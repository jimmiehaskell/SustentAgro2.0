"""BL-30 (Júlia): lista, busca, contagem por ODS e página da ONG com dados reais.
RF-01, RF-02, RF-04, RF-05, RF-06, RN-01. Testes das funções de ongs/services.py e das telas públicas."""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.tests.fabricas import criar_ods, criar_ong
from ongs.models import Necessidade, Ods
from ongs.services import buscar_ongs, ods_com_contagem, ongs_ativas, precisa_agora

SITUACOES_INATIVAS = ('pendente', 'reprovada', 'desativada')


def _ong(nome=None, nome_curto=None, **campos):
    """criar_ong não aceita nome/nome_curto; troca os dois depois de criar."""
    ong = criar_ong(**campos)
    ong.nome = nome or ong.nome
    ong.nome_curto = nome_curto or ong.nome_curto
    ong.save(update_fields=['nome', 'nome_curto'])
    return ong


def _necessidade(ong, titulo='Cestas básicas', situacao='aberta', dias_atras=0):
    necessidade = Necessidade.objects.create(ong=ong, titulo=titulo, tipo='itens', unidade='cestas',
                                             meta=Decimal('60'), situacao=situacao)
    Necessidade.objects.filter(pk=necessidade.pk).update(criada_em=timezone.now() - timedelta(days=dias_atras))
    necessidade.refresh_from_db()
    return necessidade


def _ongs_da_lista(resposta):
    return [ong for ong, _ in resposta.context['ongs']]


class SoOngAtivaTest(TestCase):  # RN-01
    def test_ongs_ativas_e_buscar_ongs_ignoram_as_outras_situacoes(self):
        ativa = criar_ong(situacao='ativa')
        for situacao in SITUACOES_INATIVAS:
            criar_ong(situacao=situacao)
        self.assertEqual(list(ongs_ativas()), [ativa])
        self.assertEqual(list(buscar_ongs()), [ativa])

    def test_lista_publica_so_mostra_ong_ativa(self):
        ativa = criar_ong(situacao='ativa')
        for situacao in SITUACOES_INATIVAS:
            criar_ong(situacao=situacao)
        self.assertEqual(_ongs_da_lista(self.client.get(reverse('ongs:lista'))), [ativa])

    def test_pagina_da_ong_abre_so_para_ong_ativa(self):
        ativa = criar_ong(situacao='ativa')
        self.assertEqual(self.client.get(reverse('ongs:detalhe', kwargs={'pk': ativa.pk})).status_code, 200)
        for situacao in SITUACOES_INATIVAS:
            with self.subTest(situacao=situacao):
                ong = criar_ong(situacao=situacao)
                resposta = self.client.get(reverse('ongs:detalhe', kwargs={'pk': ong.pk}))
                self.assertEqual(resposta.status_code, 404)


class BuscaPorTextoTest(TestCase):  # RF-01
    def test_encontra_pelo_nome_pelo_nome_curto_e_pela_cidade(self):
        ong = _ong(nome='Cozinha Solar Unida', nome_curto='Solar', localidade='Gama')
        criar_ong(localidade='Ceilândia')
        for termo in ('solar unida', 'SOLAR', 'gama'):
            with self.subTest(termo=termo):
                self.assertEqual(list(buscar_ongs(texto=termo)), [ong])

    def test_encontra_pelo_nome_do_ods_sem_diferenciar_maiusculas(self):
        Ods.objects.filter(pk=criar_ods(1).pk).update(nome='Zona Rural Viva')
        com_ods = criar_ong(ods=(1,))
        criar_ong(ods=(2,))
        self.assertEqual(list(buscar_ongs(texto='zona rural')), [com_ods])

    def test_ong_com_dois_ods_que_casam_aparece_uma_vez_so(self):  # distinct()
        Ods.objects.filter(pk=criar_ods(1).pk).update(nome='Zona Rural Um')
        Ods.objects.filter(pk=criar_ods(2).pk).update(nome='Zona Rural Dois')
        ong = criar_ong(ods=(1, 2))
        self.assertEqual(list(buscar_ongs(texto='zona rural')), [ong])

    def test_busca_da_lista_pela_querystring(self):
        ong = _ong(nome='Prato Cheio Central', nome_curto='Prato Cheio')
        criar_ong()
        resposta = self.client.get(reverse('ongs:lista'), {'q': 'prato cheio'})
        self.assertEqual(_ongs_da_lista(resposta), [ong])


class FiltrosCombinadosTest(TestCase):  # RF-04
    def test_ods_tipo_de_ajuda_e_cidade_combinam_com_e_logico(self):
        alvo = criar_ong(localidade='Gama', ods=(1, 2), aceita_itens=True)
        criar_ong(localidade='Ceilândia', ods=(1, 2), aceita_itens=True)  # cidade diferente
        criar_ong(localidade='Gama', ods=(1,), aceita_itens=True)  # sem o ODS 2
        criar_ong(localidade='Gama', ods=(1, 2), aceita_itens=False)  # não aceita itens
        resposta = self.client.get(reverse('ongs:lista'), {'ods': '2', 'tipo': 'itens', 'cidade': 'Gama'})
        self.assertEqual(_ongs_da_lista(resposta), [alvo])

    def test_filtro_por_tipo_de_ajuda(self):
        dinheiro = criar_ong(aceita_dinheiro=True, aceita_itens=False)
        criar_ong(aceita_dinheiro=False, aceita_itens=True)
        self.assertEqual(list(buscar_ongs(tipo='dinheiro')), [dinheiro])

    def test_valores_invalidos_sao_ignorados(self):
        criar_ong()
        criar_ong()
        resposta = self.client.get(reverse('ongs:lista'), {'ods': 'abc', 'tipo': 'qualquer'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(_ongs_da_lista(resposta)), 2)


class ContagemPorOdsTest(TestCase):  # RF-02
    def test_conta_so_ongs_ativas(self):
        criar_ong(situacao='ativa', ods=(1, 2))
        criar_ong(situacao='ativa', ods=(1,))
        criar_ong(situacao='pendente', ods=(1,))  # no mesmo ODS, mas não entra
        contagem = {ods.numero: ods.total for ods in ods_com_contagem()}
        self.assertEqual(contagem[1], 2)
        self.assertEqual(contagem[2], 1)

    def test_total_do_cartao_bate_com_a_lista_filtrada(self):
        criar_ong(situacao='ativa', ods=(1, 2))
        criar_ong(situacao='ativa', ods=(2,))
        criar_ong(situacao='desativada', ods=(2,))
        for ods in ods_com_contagem():
            with self.subTest(ods=ods.numero):
                resposta = self.client.get(reverse('ongs:lista'), {'ods': ods.numero})
                self.assertEqual(len(_ongs_da_lista(resposta)), ods.total)

    def test_inicio_mostra_a_contagem_real(self):
        criar_ong(situacao='ativa', ods=(1,))
        criar_ong(situacao='pendente', ods=(1,))
        resposta = self.client.get(reverse('core:inicio'))
        contagem = {ods.numero: total for ods, total in resposta.context['ods_com_contagem']}
        self.assertEqual(contagem[1], 1)


class PrecisaAgoraTest(TestCase):  # RF-05
    def test_devolve_a_necessidade_aberta_mais_recente(self):
        ong = criar_ong()
        _necessidade(ong, 'Antiga', dias_atras=5)
        nova = _necessidade(ong, 'Nova', dias_atras=1)
        self.assertEqual(precisa_agora(ong), nova)

    def test_ignora_atendida_e_encerrada(self):
        ong = criar_ong()
        _necessidade(ong, 'Atendida', situacao='atendida', dias_atras=0)
        _necessidade(ong, 'Encerrada', situacao='encerrada', dias_atras=0)
        aberta = _necessidade(ong, 'Aberta', dias_atras=10)
        self.assertEqual(precisa_agora(ong), aberta)

    def test_sem_necessidade_aberta_devolve_none(self):
        ong = criar_ong()
        self.assertIsNone(precisa_agora(ong))
        _necessidade(ong, situacao='atendida')
        self.assertIsNone(precisa_agora(ong))

    def test_cartao_da_lista_traz_a_necessidade_de_cada_ong(self):
        ong = criar_ong()
        _necessidade(ong, 'Gas de cozinha')
        resposta = self.client.get(reverse('ongs:lista'))
        self.assertEqual([precisa.titulo for _, precisa in resposta.context['ongs']], ['Gas de cozinha'])


class PaginaDaOngTest(TestCase):  # RF-06
    def test_mostra_abertas_e_atendidas_e_esconde_as_encerradas(self):
        ong = criar_ong()
        _necessidade(ong, 'Necessidade aberta', situacao='aberta')
        _necessidade(ong, 'Necessidade atendida', situacao='atendida')
        _necessidade(ong, 'Necessidade encerrada', situacao='encerrada')
        resposta = self.client.get(reverse('ongs:detalhe', kwargs={'pk': ong.pk}))
        self.assertContains(resposta, 'Necessidade aberta')
        self.assertContains(resposta, 'Necessidade atendida')
        self.assertNotContains(resposta, 'Necessidade encerrada')