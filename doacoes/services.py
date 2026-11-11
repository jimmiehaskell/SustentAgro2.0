"""Regras de doação e voluntariado (camada 2, BL-42 a BL-45)."""
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from contas.choices import TipoConta
from contas.models import PerfilPessoa
from doacoes.choices import SituacaoContribuicao, TipoContribuicao
from doacoes.models import Contribuicao
from ongs.choices import SituacaoNecessidade, SituacaoOng
from ongs.models import Necessidade, Ong


def registrar_contribuicao(pessoa, ong, tipo, quantidade, necessidade=None):
    """RF-14, RF-15: registra itens ou inscrição pendentes (RN-02)."""
    if tipo not in (TipoContribuicao.ITENS, TipoContribuicao.VOLUNTARIADO):
        raise ValidationError('Tipo de contribuição indisponível.')
    try:
        valor = Decimal(str(quantidade))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError('Informe uma quantidade válida.') from None
    if not valor.is_finite() or valor <= 0 or valor.as_tuple().exponent < -2 or valor >= Decimal('100000000'):
        raise ValidationError('Informe uma quantidade positiva com até duas casas decimais.')
    if tipo == TipoContribuicao.VOLUNTARIADO and valor != 1:
        raise ValidationError('Cada inscrição corresponde a uma pessoa.')
    if pessoa is None or pessoa.pk is None:
        raise ValidationError('É necessário um perfil de doador para contribuir.')
    if ong is None or ong.pk is None:
        raise ValidationError('A ONG não está apta a receber contribuições.')
    if necessidade is None or necessidade.pk is None:
        raise ValidationError('Selecione uma necessidade.')
    with transaction.atomic():
        pessoa_atual = PerfilPessoa.objects.select_related('usuario').filter(pk=pessoa.pk).first()
        ong_atual = Ong.objects.select_for_update().filter(pk=ong.pk).first()
        if pessoa_atual is None or pessoa_atual.usuario.tipo_conta != TipoConta.PESSOA or not pessoa_atual.eh_doador:
            raise ValidationError('É necessário um perfil de doador para contribuir.')
        if ong_atual is None or ong_atual.situacao != SituacaoOng.ATIVA:
            raise ValidationError('A ONG não está apta a receber contribuições.')
        if not getattr(ong_atual, f'aceita_{tipo}'):
            raise ValidationError('A ONG não aceita este tipo de contribuição.')
        atual = Necessidade.objects.select_for_update().filter(pk=necessidade.pk).first()
        if atual is None or atual.ong_id != ong_atual.pk:
            raise ValidationError('Necessidade não encontrada para esta ONG.')
        if atual.tipo != tipo or atual.situacao != SituacaoNecessidade.ABERTA:
            raise ValidationError('Esta necessidade não aceita a contribuição.')
        contribuicao = Contribuicao(pessoa=pessoa_atual, ong=ong_atual, necessidade=atual, tipo=tipo,
                                   quantidade=valor, situacao=SituacaoContribuicao.PENDENTE)
        contribuicao.full_clean()
        contribuicao.save()
    return contribuicao


def confirmar_contribuicao(contribuicao, quantidade_confirmada):
    """RF-16, RN-02 (BL-44). A barra da necessidade só avança com o que a ONG confirmou."""
    raise NotImplementedError('BL-44')


def recusar_contribuicao(contribuicao):
    """RF-16 (BL-44). situacao = recusada; a barra não muda."""
    raise NotImplementedError('BL-44')


def cancelar_contribuicao(contribuicao):
    """RF-26, P-07 (BL-45). Só pendente; situacao = cancelada."""
    raise NotImplementedError('BL-45')
