"""Regras de negócio do app ongs (ADR-001). Views e ações do admin só chamam estas funções."""
import re
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone


from colheita.choices import CanceladaPor, SituacaoReserva
from ongs.choices import SituacaoNecessidade, SituacaoOng, TipoNecessidade

# RNF-06: limite de tamanho das imagens (o mesmo do Nginx do servidor)
TAMANHO_MAXIMO_DA_IMAGEM = 10 * 1024 * 1024

# RF-10: pesos do cálculo dos dois dígitos verificadores do CNPJ
_PESOS_DO_1O_DIGITO = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_PESOS_DO_2O_DIGITO = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


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


def _digito_verificador(numeros, pesos):
    resto = sum(int(numero) * peso for numero, peso in zip(numeros, pesos)) % 11
    return '0' if resto < 2 else str(11 - resto)


def validar_cnpj(cnpj):
    """RF-10 (BL-29, Vinicius). Devolve True se o CNPJ tem 14 dígitos e dígitos verificadores válidos.

    Aceita o número com ou sem pontuação ("11.222.333/0001-81" ou "11222333000181").
    Sequências repetidas ("00000000000000") são inválidas.
    A unicidade é garantida pelo unique=True do campo Ong.cnpj.
    Testes: ongs/tests/test_cnpj.py
    """
    digitos = re.sub(r'[.\-/\s]', '', cnpj or '')
    if len(digitos) != 14 or not digitos.isdigit() or len(set(digitos)) == 1:
        return False
    primeiro = _digito_verificador(digitos[:12], _PESOS_DO_1O_DIGITO)
    segundo = _digito_verificador(digitos[:12] + primeiro, _PESOS_DO_2O_DIGITO)
    return digitos[12:] == primeiro + segundo


def aprovar_ong(ong):
    """RN-14, RF-11 (BL-29, Júlia): situacao = ativa e aprovada_em = agora.
    Apaga o motivo de uma reprovação anterior. Testes: ongs/tests/test_situacao.py
    """
    ong.situacao = SituacaoOng.ATIVA
    ong.aprovada_em = timezone.now()
    ong.motivo_reprovacao = ''
    ong.save(update_fields=['situacao', 'aprovada_em', 'motivo_reprovacao'])


def reprovar_ong(ong, motivo):
    """RN-14, RN-20 (BL-29, Júlia): situacao = reprovada e grava o motivo, que a ONG vê ao entrar.
    Sem motivo, levanta ValidationError. Testes: ongs/tests/test_situacao.py
    """
    motivo = (motivo or '').strip()
    if not motivo:
        raise ValidationError({'motivo_reprovacao': 'Informe o motivo da reprovação.'})
    ong.situacao = SituacaoOng.REPROVADA
    ong.motivo_reprovacao = motivo
    ong.save(update_fields=['situacao', 'motivo_reprovacao'])


def desativar_ong(ong):
    """RN-14, RN-19, E-05 (BL-29, Júlia): situacao = desativada e cancela as reservas ativas da ONG
    (cancelada_por = sistema), devolvendo as quantidades ao saldo das ofertas.

    O saldo é calculado (colheita.services.saldo), então basta cancelar as reservas. Devolve quantas
    reservas foram canceladas, para o admin avisar. Testes: ongs/tests/test_situacao.py
    """
    from colheita.models import Reserva  # dentro da função: ongs.models importa este módulo

    with transaction.atomic():
        canceladas = Reserva.objects.filter(ong=ong, situacao=SituacaoReserva.ATIVA).update(
            situacao=SituacaoReserva.CANCELADA, cancelada_por=CanceladaPor.SISTEMA)
        ong.situacao = SituacaoOng.DESATIVADA
        ong.save(update_fields=['situacao'])
    return canceladas


def ongs_ativas():
    """RN-01 (BL-30). Só ONG ativa (aprovada e não desativada) aparece em telas públicas."""
    from ongs.models import Ong  # dentro da função: ongs.models importa este módulo

    return Ong.objects.filter(situacao=SituacaoOng.ATIVA)


def buscar_ongs(texto='', ods='', tipo='', cidade=''):
    """RF-01, RF-04 (BL-30). ONGs ativas filtradas por texto, ODS, tipo de ajuda e cidade (E lógico).

    O texto procura no nome, no nome curto, no slogan, na descrição, na cidade e no nome dos ODS.
    """
    ongs = ongs_ativas()
    texto = (texto or '').strip()
    if texto:
        ongs = ongs.filter(
            Q(nome__icontains=texto) | Q(nome_curto__icontains=texto) | Q(slogan__icontains=texto)
            | Q(descricao__icontains=texto) | Q(localidade__nome__icontains=texto)
            | Q(ods__nome__icontains=texto))
    if str(ods).isdigit():
        ongs = ongs.filter(ods__numero=int(ods))
    if tipo in TipoNecessidade.values:
        ongs = ongs.filter(**{f'aceita_{tipo}': True})
    if cidade:
        ongs = ongs.filter(localidade__nome=cidade)
    return ongs.select_related('localidade').prefetch_related('ods', 'necessidades').distinct().order_by('nome')


def precisa_agora(ong):
    """RF-05 (BL-30). Necessidade aberta mais recente da ONG (Necessidade já vem ordenada por -criada_em)."""
    return next((n for n in ong.necessidades.all() if n.situacao == SituacaoNecessidade.ABERTA), None)


def ods_com_contagem():
    """RF-02 (BL-30). Os ODS com `total` = quantidade de ONGs ativas de cada um."""
    from ongs.models import Ods  # dentro da função: ongs.models importa este módulo

    return Ods.objects.annotate(total=Count('ongs', filter=Q(ongs__situacao=SituacaoOng.ATIVA)))