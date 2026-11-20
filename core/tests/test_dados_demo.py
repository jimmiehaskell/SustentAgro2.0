"""BL-27 (Pedro): coerência dos dados da carga de demonstração. RF-32, RN-13, RN-16, RN-24, P-06, E-10.

Conferem só os dados (core/demo/dados.py), sem banco: o comando que grava entra depois do BL-24 ao BL-26.
"""
from collections import defaultdict
from decimal import Decimal

from django.test import SimpleTestCase

from colheita.choices import Categoria, Destino, Estado, Transporte, Unidade
from contas.choices import UF
from core.demo import dados
from core.demo.cnpj import digitos_verificadores
from ongs.choices import SituacaoNecessidade, SituacaoOng, TipoNecessidade

NOMES_LOCALIDADES = {nome for nome, *_ in dados.LOCALIDADES}
NUMEROS_ODS = {numero for numero, *_ in dados.ODS}
ONG_POR_CHAVE = {ong['chave']: ong for ong in dados.ONGS}
AGRICULTORES = {a['username'] for a in dados.AGRICULTORES}
TODAS_AS_OFERTAS = dados.OFERTAS_ABERTAS + dados.HISTORICO


class LocalidadesTest(SimpleTestCase):  # P-06
    def test_nomes_unicos_e_uf_valida(self):
        self.assertEqual(len(NOMES_LOCALIDADES), len(dados.LOCALIDADES))
        for nome, uf, *_ in dados.LOCALIDADES:
            self.assertIn(uf, UF.values, nome)

    def test_coordenadas_dentro_do_df_e_entorno(self):
        for nome, _, latitude, longitude in dados.LOCALIDADES:
            self.assertTrue(Decimal('-16.5') < latitude < Decimal('-15.3'), nome)
            self.assertTrue(Decimal('-48.5') < longitude < Decimal('-47.2'), nome)

    def test_toda_localidade_usada_existe(self):
        usadas = [ong['localidade'] for ong in dados.ONGS]
        usadas += [p['localidade'] for p in dados.AGRICULTORES + dados.DOADORES if p['localidade']]
        usadas += [oferta['localidade'] for oferta in TODAS_AS_OFERTAS]
        for nome in usadas:
            self.assertIn(nome, NOMES_LOCALIDADES)


class PessoasEOngsTest(SimpleTestCase):
    def test_nomes_de_usuario_unicos(self):
        usernames = [p['username'] for p in dados.AGRICULTORES + dados.DOADORES + dados.ONGS]
        self.assertEqual(len(usernames), len(set(usernames)))

    def test_agricultor_tem_localidade(self):  # obrigatória para agricultor (BL-24)
        for agricultor in dados.AGRICULTORES:
            self.assertTrue(agricultor['localidade'], agricultor['username'])

    def test_cnpjs_validos_e_unicos(self):  # RN-24, E-11
        cnpjs = [ong['cnpj'] for ong in dados.ONGS]
        self.assertEqual(len(cnpjs), len(set(cnpjs)))
        for cnpj in cnpjs:
            self.assertEqual(len(cnpj), 14)
            self.assertEqual(cnpj[12:], digitos_verificadores(cnpj[:12]))

    def test_nomes_de_ong_unicos(self):  # nome e nome_curto são unique no model
        self.assertEqual(len({o['nome'] for o in dados.ONGS}), len(dados.ONGS))
        self.assertEqual(len({o['nome_curto'] for o in dados.ONGS}), len(dados.ONGS))

    def test_situacoes_e_ods_validos(self):
        for ong in dados.ONGS:
            self.assertIn(ong['situacao'], SituacaoOng.values)
            self.assertTrue(ong['ods'], ong['nome'])                       # pelo menos 1 ODS
            self.assertTrue(set(ong['ods']) <= NUMEROS_ODS, ong['nome'])
        reprovadas = [o for o in dados.ONGS if o['situacao'] == 'reprovada']
        self.assertTrue(reprovadas)
        self.assertTrue(all(o['motivo_reprovacao'] for o in reprovadas))  # RN-20: motivo aparece para a ONG

    def test_necessidade_so_de_tipo_que_a_ong_aceita(self):  # A-04
        for ong in dados.ONGS:
            for necessidade in ong['necessidades']:
                self.assertIn(necessidade['tipo'], TipoNecessidade.values)
                self.assertIn(necessidade['situacao'], SituacaoNecessidade.values)
                self.assertTrue(ong[f"aceita_{necessidade['tipo']}"], necessidade['titulo'])

    def test_ha_necessidades_para_as_telas(self):  # A-01: na camada 1, a carga é a única fonte de necessidades
        abertas = [n for o in dados.ONGS for n in o['necessidades'] if n['situacao'] == 'aberta']
        self.assertGreaterEqual(len(abertas), 8)


class OfertasEReservasTest(SimpleTestCase):
    def test_valores_das_listas_fixas(self):
        for oferta in TODAS_AS_OFERTAS:
            self.assertIn(oferta['agricultor'], AGRICULTORES)
            self.assertIn(oferta['categoria'], Categoria.values)
            self.assertIn(oferta['unidade'], Unidade.values)
            self.assertIn(oferta['estado'], Estado.values)
            self.assertIn(oferta['destino'], Destino.values)
            self.assertIn(oferta['transporte'], Transporte.values)

    def test_preco_so_em_venda(self):  # RN-13
        for oferta in TODAS_AS_OFERTAS:
            self.assertEqual(oferta['destino'] == 'vender', oferta['preco_unitario'] is not None, oferta['produto'])

    def test_unidades_sem_fracao(self):  # RN-16
        for oferta in TODAS_AS_OFERTAS:
            if oferta['unidade'] == 'un':
                self.assertEqual(oferta['quantidade'] % 1, 0, oferta['produto'])
                for reserva in oferta['reservas']:
                    self.assertEqual(reserva['quantidade'] % 1, 0, oferta['produto'])

    def test_reservas_nao_passam_da_oferta(self):  # RN-03: saldo nunca negativo
        for oferta in TODAS_AS_OFERTAS:
            reservado = sum(r['quantidade'] for r in oferta['reservas'])
            self.assertLessEqual(reservado, oferta['quantidade'], oferta['produto'])
            for reserva in oferta['reservas']:
                self.assertLessEqual(reserva.get('quantidade_recebida', 0), reserva['quantidade'])

    def test_so_ong_ativa_reserva_ou_recebe_oferta_direcionada(self):  # RN-01
        for oferta in TODAS_AS_OFERTAS:
            for reserva in oferta['reservas']:
                self.assertEqual(ONG_POR_CHAVE[reserva['ong']]['situacao'], 'ativa')
            if oferta.get('ong_destino'):
                self.assertEqual(ONG_POR_CHAVE[oferta['ong_destino']]['situacao'], 'ativa')

    def test_ofertas_abertas_nao_estao_vencidas(self):
        for oferta in dados.OFERTAS_ABERTAS:
            self.assertGreaterEqual(oferta['colher_em_dias'], 1, oferta['produto'])
            self.assertTrue(all(r['situacao'] == 'ativa' for r in oferta['reservas']))

    def test_historico_so_tem_reservas_recebidas(self):
        for oferta in dados.HISTORICO:
            self.assertTrue(oferta['reservas'], oferta['produto'])
            self.assertTrue(all(r['situacao'] == 'recebida' for r in oferta['reservas']))
            self.assertTrue(0 <= oferta['meses_atras'] <= 5 and 1 <= oferta['dia'] <= 28)


class PainelTest(SimpleTestCase):  # o histórico tem que dar um painel com conteúdo (RF-29 a RF-31)
    def test_kg_recebidos_por_mes_iguais_ao_grafico_mock(self):  # RN-08: só kg
        kg_por_mes = defaultdict(Decimal)
        for oferta in dados.HISTORICO:
            if oferta['unidade'] == 'kg':
                kg_por_mes[oferta['meses_atras']] += sum(r['quantidade_recebida'] for r in oferta['reservas'])
        self.assertEqual([kg_por_mes[m] for m in range(5, -1, -1)], [320, 540, 610, 880, 1130, 900])

    def test_varios_ods_recebem_colheita(self):  # E-10
        ods = {n for oferta in dados.HISTORICO for r in oferta['reservas'] for n in ONG_POR_CHAVE[r['ong']]['ods']}
        self.assertGreaterEqual(len(ods), 4)

    def test_ha_renda_gerada(self):  # RN-09
        vendas = [o for o in dados.HISTORICO if o['destino'] == 'vender']
        self.assertTrue(vendas)
