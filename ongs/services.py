"""Regras de negócio do app ongs (ADR-001). Views e ações do admin só chamam estas funções."""
from django.db import transaction
from django.utils import timezone


def validar_cnpj(cnpj):
    """RF-10 (BL-29, Vinicius). Devolve True se o CNPJ tem 14 dígitos e dígitos verificadores válidos.

    Aceita o número com ou sem pontuação ("11.222.333/0001-81" ou "11222333000181").
    Sequências repetidas ("00000000000000") são inválidas.
    A unicidade é garantida pelo unique=True do campo Ong.cnpj.
    Testes: ongs/tests/test_cnpj.py
    """
    raise NotImplementedError('BL-29')


def aprovar_ong(ong):
    """RN-14, RF-11 (BL-29, Júlia): situacao = ativa e aprovada_em = agora."""
    ong.situacao = 'ativa'
    ong.aprovada_em = timezone.now()
    ong.motivo_reprovacao = ''
    ong.save(update_fields=['situacao', 'aprovada_em', 'motivo_reprovacao'])



def reprovar_ong(ong, motivo):
    """RN-14, RN-20 (BL-29, Júlia): situacao = reprovada e grava o motivo, que a ONG vê ao entrar."""
    if not motivo or not motivo.strip():
        raise ValueError('Informe o motivo da reprovação.')
    ong.situacao = 'reprovada'
    ong.motivo_reprovacao = motivo
    ong.save(update_fields=['situacao', 'motivo_reprovacao'])



def desativar_ong(ong):
    """RN-14, RN-19, E-05 (BL-29, Júlia): situacao = desativada e cancela as reservas ativas da ONG
    (cancelada_por = sistema), devolvendo as quantidades ao saldo das ofertas."""
    from colheita.models import Reserva
    with transaction.atomic():
        Reserva.objects.filter(ong=ong, situacao='ativa').update(situacao='cancelada', cancelada_por='sistema')
        ong.situacao = 'desativada'
        ong.save(update_fields=['situacao'])
