"""Regras de negócio da Colheita Solidária (ADR-001, ADR-003).

Toda função que muda dados levanta django.core.exceptions.ValidationError com uma mensagem em
português quando a regra não é atendida; a view mostra essa mensagem para a pessoa.
"""
import math
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Sum

from colheita.choices import Destino, SituacaoReserva, Unidade

RAIO_DA_TERRA_KM = 6371.0


def distancia_km(origem, destino):
    """RN-15 (BL-33, Gabriel). Distância em linha reta (fórmula de haversine) entre duas localidades,
    usando latitude e longitude. Mesma localidade = 0. Devolve float arredondado para 1 casa.
    Testes: colheita/tests/test_distancia.py
    """
    lat1, lon1 = math.radians(origem.latitude), math.radians(origem.longitude)
    lat2, lon2 = math.radians(destino.latitude), math.radians(destino.longitude)
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return round(2 * RAIO_DA_TERRA_KM * math.asin(math.sqrt(a)), 1)


def saldo(oferta):
    """RN-03 (BL-26). Quantidade publicada menos a soma das reservas ativas e recebidas.
    Reservas canceladas e não recebidas não contam. Nunca negativo.
    A recebida conta pela quantidade reservada: a diferença para o recebido não volta ao saldo.
    Testes: colheita/tests/test_models.py
    """
    if oferta.pk is None:
        return oferta.quantidade
    reservado = oferta.reservas.filter(
        situacao__in=[SituacaoReserva.ATIVA, SituacaoReserva.RECEBIDA],
    ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')
    return max(oferta.quantidade - reservado, Decimal('0'))


def validar_oferta(oferta, checar_data=True):
    """RN-13, RN-16, UC-08 (BL-32, Gabriel). Levanta ValidationError se:
    - destino = vender sem preço, ou destino = doar com preço;
    - unidade = un com quantidade fracionada;
    - colher_ate no passado.
    Também recusa quantidade ou preço menores ou iguais a zero. Os erros saem por campo, para o
    formulário mostrar cada mensagem ao lado do campo certo.
    checar_data=False pula a data, para editar uma oferta antiga (Oferta.clean, BL-26). Campos vazios
    são ignorados aqui: o próprio campo do model já avisa que é obrigatório.
    Testes: colheita/tests/test_oferta.py
    """
    erros = {}

    if oferta.quantidade is None:
        pass
    elif oferta.quantidade <= 0:
        erros['quantidade'] = 'Informe uma quantidade maior que zero.'
    else:
        erro_fracao = erro_de_fracao(oferta.quantidade, oferta.unidade)
        if erro_fracao:
            erros['quantidade'] = erro_fracao

    if oferta.destino == Destino.VENDER:
        if oferta.preco_unitario is None:
            erros['preco_unitario'] = 'Informe o preço para vender a oferta.'
        elif oferta.preco_unitario <= 0:
            erros['preco_unitario'] = 'O preço precisa ser maior que zero.'
    elif oferta.preco_unitario is not None:
        erros['preco_unitario'] = 'Oferta de doação não tem preço.'

    # Mesma referência de "hoje" dos testes (date.today(), relógio do sistema)
    if checar_data and oferta.colher_ate is not None and oferta.colher_ate < date.today():
        erros['colher_ate'] = 'A data "colher até" não pode estar no passado.'

    if erros:
        raise ValidationError(erros)


def erro_de_fracao(quantidade, unidade):
    """RN-16, E-01. Devolve a mensagem de erro se a quantidade tem mais casas decimais do que a unidade
    aceita (kg: uma casa; un: só inteiros), ou None se está certa. Serve também à reserva e ao recebimento.
    """
    if unidade == Unidade.UN and quantidade != quantidade.to_integral_value():
        return 'Em unidades, informe só números inteiros.'
    if unidade == Unidade.KG and quantidade != quantidade.quantize(Decimal('0.1')):
        return 'Em kg, informe no máximo uma casa decimal.'
    return None


def validar_quantidade_da_reserva(reserva):
    """RN-16, E-01, E-02 (BL-26). Reservada maior que zero e, se informada, recebida de 0 até a reservada,
    nas casas decimais da unidade da oferta. Não confere o saldo: isso é do reservar_oferta (BL-34),
    que trava a oferta antes de somar as reservas.
    """
    if reserva.oferta_id is None or reserva.quantidade is None:
        return  # o próprio campo do model já avisa que é obrigatório
    unidade = reserva.oferta.unidade
    erros = {}

    if reserva.quantidade <= 0:
        erros['quantidade'] = 'Informe uma quantidade maior que zero.'
    elif erro_de_fracao(reserva.quantidade, unidade):
        erros['quantidade'] = erro_de_fracao(reserva.quantidade, unidade)

    recebida = reserva.quantidade_recebida
    if recebida is not None:
        if recebida < 0 or recebida > reserva.quantidade:
            erros['quantidade_recebida'] = 'A quantidade recebida vai de 0 até a reservada.'
        elif erro_de_fracao(recebida, unidade):
            erros['quantidade_recebida'] = erro_de_fracao(recebida, unidade)

    if erros:
        raise ValidationError(erros)


def reservar_oferta(oferta, ong, quantidade):
    """RF-20, RN-01, RN-03, RN-16, UC-09 (BL-34, Gabriel em dupla com Jimmie).

    Dentro de transaction.atomic(), trava a oferta com select_for_update(), recalcula o saldo e cria a
    Reserva. Levanta ValidationError se a ONG não está ativa, se a quantidade é <= 0, se passa do saldo
    ("Só restam X kg desta oferta.") ou se é fracionada numa oferta em unidades. Devolve a Reserva.
    Testes: colheita/tests/test_reserva.py
    """
    raise NotImplementedError('BL-34')


def confirmar_recebimento(reserva, quantidade_recebida):
    """RF-23, RN-17, RN-18, E-02, E-03 (BL-35, Gabriel em dupla com Jimmie).

    Aceita de 0 até reserva.quantidade. Acima disso: ValidationError.
    Maior que 0: situacao = recebida, grava quantidade_recebida e recebida_em (agora).
    Igual a 0: situacao = nao_recebida; a quantidade volta ao saldo (só se a oferta não venceu).
    Testes: colheita/tests/test_recebimento.py
    """
    raise NotImplementedError('BL-35')


def cancelar_reserva(reserva, cancelada_por):
    """RF-24 (BL-47, camada 3). Só reserva ativa; situacao = cancelada; a quantidade volta ao saldo."""
    raise NotImplementedError('BL-47')
