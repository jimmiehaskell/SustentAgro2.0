"""Regras de negócio do app ongs (ADR-001). Views e ações do admin só chamam estas funções."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ongs.choices import SituacaoNecessidade

# RNF-06: limite de tamanho das imagens (o mesmo do Nginx do servidor)
TAMANHO_MAXIMO_DA_IMAGEM = 10 * 1024 * 1024


def validar_tamanho_da_imagem(arquivo):
    """RNF-06 (BL-25). Recusa imagem com mais de 10 MB. Usado como validador do logo e da capa da ONG.
    Testes: ongs/tests/test_models_ongs.py
    """
    if arquivo.size > TAMANHO_MAXIMO_DA_IMAGEM:
        raise ValidationError('A imagem deve ter no máximo 10 MB.')


def confirmado_da_necessidade(necessidade):
    """RN-02 (BL-25). Quantidade ou valor já confirmado pela ONG; promessas e inscrições pendentes não contam.

    As contribuições só existem na camada 2 (doacoes.Contribuicao, BL-42 a BL-45). Até lá, nada é
    confirmado e as barras começam em zero.
    Testes: ongs/tests/test_models_ongs.py
    """
    return Decimal('0')


def percentual_da_necessidade(necessidade):
    """RN-21 (BL-25). Percentual da meta já confirmado, de 0 a 100, como nos mocks.

    Necessidade atendida fica com a barra em 100%, mesmo antes de existirem contribuições confirmadas.
    Testes: ongs/tests/test_models_ongs.py
    """
    if necessidade.situacao == SituacaoNecessidade.ATENDIDA:
        return 100
    if not necessidade.meta:
        return 0
    return min(100, int(confirmado_da_necessidade(necessidade) / necessidade.meta * 100))


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
