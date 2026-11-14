"""Grava no banco os dados de demonstração de core/demo/dados.py (BL-27 parte 3, Pedro). RF-32, RN-24.

Apaga e recria pessoas, ONGs, necessidades, ofertas e reservas. Localidades e ODS são atualizados pelo
nome e pelo número, sem apagar, porque o administrador também pode editá-los (P-06, A-05).
Superusuários e contas da equipe (is_staff) nunca são apagados.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from colheita.models import Oferta, Reserva
from contas.models import Localidade, PerfilPessoa, Usuario
from core.demo import dados
from ongs.models import Necessidade, Ods, Ong

HORARIO_DO_RECEBIMENTO = 10  # 10h da manhã, no horário de Brasília


def carregar(senha):
    """Recria os dados de demonstração e devolve um dicionário com quantos registros de cada tipo existem."""
    with transaction.atomic():
        _apagar()
        localidades = _carregar_localidades()
        ods = _carregar_ods()
        perfis = _carregar_pessoas(senha, localidades)
        ongs = _carregar_ongs(senha, localidades, ods)
        _carregar_ofertas_abertas(perfis, ongs, localidades)
        _carregar_historico(perfis, ongs, localidades)
    return {
        'localidades': Localidade.objects.count(), 'ods': Ods.objects.count(),
        'pessoas': PerfilPessoa.objects.count(), 'ongs': Ong.objects.count(),
        'necessidades': Necessidade.objects.count(), 'ofertas': Oferta.objects.count(),
        'reservas': Reserva.objects.count(),
    }


def _apagar():
    # Na ordem certa: primeiro quem aponta para os outros (reservas → ofertas → ONGs e pessoas)
    Reserva.objects.all().delete()
    Oferta.objects.all().delete()
    Necessidade.objects.all().delete()
    Ong.objects.all().delete()
    PerfilPessoa.objects.all().delete()
    Usuario.objects.filter(is_superuser=False, is_staff=False).delete()


def _carregar_localidades():
    localidades = {}
    for nome, uf, latitude, longitude in dados.LOCALIDADES:
        localidades[nome], _ = Localidade.objects.update_or_create(
            nome=nome, defaults={'uf': uf, 'latitude': latitude, 'longitude': longitude})
    return localidades


def _carregar_ods():
    ods = {}
    for numero, nome, cor in dados.ODS:
        ods[numero], _ = Ods.objects.update_or_create(numero=numero, defaults={'nome': nome, 'cor': cor})
    return ods


def _criar_usuario(username, nome, email, senha, tipo_conta):
    primeiro, _, resto = nome.partition(' ')
    return Usuario.objects.create_user(username=username, email=email, password=senha, tipo_conta=tipo_conta,
                                       first_name=primeiro, last_name=resto)


def _carregar_pessoas(senha, localidades):
    perfis = {}
    for pessoa, eh_agricultor in [(p, True) for p in dados.AGRICULTORES] + [(p, False) for p in dados.DOADORES]:
        usuario = _criar_usuario(pessoa['username'], pessoa['nome_completo'], pessoa['email'], senha, 'pessoa')
        perfis[pessoa['username']] = PerfilPessoa.objects.create(
            usuario=usuario, nome_completo=pessoa['nome_completo'], telefone=pessoa['telefone'],
            eh_agricultor=eh_agricultor, eh_doador=not eh_agricultor,
            localidade=localidades.get(pessoa['localidade']))
    return perfis


def _carregar_ongs(senha, localidades, ods):
    ongs = {}
    agora = timezone.now()
    campos_simples = ['nome', 'nome_curto', 'cnpj', 'slogan', 'descricao', 'telefone', 'email_contato',
                      'chave_pix', 'familias_por_mes', 'aceita_itens', 'aceita_dinheiro', 'aceita_voluntariado',
                      'situacao', 'motivo_reprovacao']
    for dado in dados.ONGS:
        usuario = _criar_usuario(dado['username'], dado['nome'], dado['email_contato'], senha, 'ong')
        ativa = dado['situacao'] == 'ativa'
        ong = Ong(usuario=usuario, localidade=localidades[dado['localidade']],
                  verificacao_cnpj='confirmado' if ativa else 'nao_consultado',
                  aprovada_em=agora - timedelta(days=60) if ativa else None,
                  **{campo: dado[campo] for campo in campos_simples})
        ong.save()
        ong.ods.set([ods[numero] for numero in dado['ods']])
        for necessidade in dado['necessidades']:
            Necessidade.objects.create(ong=ong, **necessidade)
        ongs[dado['chave']] = ong
    return ongs


def _nova_oferta(dado, perfis, ongs, localidades, colher_ate):
    return Oferta.objects.create(
        agricultor=perfis[dado['agricultor']], categoria=dado['categoria'], produto=dado['produto'],
        quantidade=dado['quantidade'], unidade=dado['unidade'], colher_ate=colher_ate,
        localidade=localidades[dado['localidade']], estado=dado['estado'], destino=dado['destino'],
        preco_unitario=dado['preco_unitario'], local_retirada=dado['local_retirada'],
        transporte=dado['transporte'], ong_destino=ongs.get(dado.get('ong_destino')))


def _carregar_ofertas_abertas(perfis, ongs, localidades):
    hoje = timezone.localdate()
    for dado in dados.OFERTAS_ABERTAS:
        oferta = _nova_oferta(dado, perfis, ongs, localidades, hoje + timedelta(days=dado['colher_em_dias']))
        for reserva in dado['reservas']:
            Reserva.objects.create(oferta=oferta, ong=ongs[reserva['ong']], quantidade=reserva['quantidade'],
                                   situacao=reserva['situacao'])


def data_do_recebimento(meses_atras, dia, hoje):
    """O dia do recebimento no histórico, contando os meses a partir de hoje (no horário de Brasília).
    No mês atual, nunca passa de hoje, para não haver recebimento no futuro."""
    mes = hoje.month - meses_atras
    ano = hoje.year
    while mes < 1:
        mes += 12
        ano -= 1
    if meses_atras == 0:
        dia = min(dia, hoje.day)
    return datetime(ano, mes, dia, HORARIO_DO_RECEBIMENTO, tzinfo=ZoneInfo(settings.TIME_ZONE))


def _carregar_historico(perfis, ongs, localidades):
    hoje = timezone.localdate()
    for dado in dados.HISTORICO:
        recebida_em = data_do_recebimento(dado['meses_atras'], dado['dia'], hoje)
        criada_em = recebida_em - timedelta(days=5)
        oferta = _nova_oferta(dado, perfis, ongs, localidades, (recebida_em - timedelta(days=2)).date())
        # criada_em tem auto_now_add: só dá para colocar uma data no passado depois de criar
        Oferta.objects.filter(pk=oferta.pk).update(criada_em=criada_em, aberta_a_todas_em=criada_em)
        for reserva in dado['reservas']:
            nova = Reserva.objects.create(
                oferta=oferta, ong=ongs[reserva['ong']], quantidade=reserva['quantidade'],
                situacao=reserva['situacao'], quantidade_recebida=reserva['quantidade_recebida'],
                recebida_em=recebida_em)
            Reserva.objects.filter(pk=nova.pk).update(criada_em=criada_em + timedelta(days=1))
