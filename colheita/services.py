"""Regras de negócio da Colheita Solidária (ADR-001, ADR-003).

Toda função que muda dados levanta django.core.exceptions.ValidationError com uma mensagem em
português quando a regra não é atendida; a view mostra essa mensagem para a pessoa.
"""
import math
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.formats import number_format

from colheita.choices import Destino, SituacaoOferta, SituacaoReserva, Unidade
from ongs.choices import SituacaoOng

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


def ofertas_da_lista(ong=None, limite_km=None):
    """RF-19, RF-28, RN-04, RN-05, RN-15, RN-18, RN-22, P-03 (BL-33, Gabriel). Ofertas da Tela 7.
    Só entram ofertas abertas, não vencidas e com saldo: a vencida sai da lista, mas as reservas dela
    continuam valendo (RN-18). Aparece para todos a oferta já aberta a todas (aberta_a_todas_em <= agora:
    sem ONG de destino, desde a publicação, RN-05; direcionada, 48 h depois, RN-04); antes disso, só para a
    ONG de destino.
    Com ong (ativa): põe distancia_km em cada oferta, aplica limite_km (None = todas) e ordena (RF-22):
    as exclusivas da ONG primeiro, depois as urgentes (RN-06), depois do mais perto para o mais longe.
    Sem ong (visitante e doador): sem distância, sem filtro de km e sem selo ou ordem de urgência (P-05).
    Testes: colheita/tests/test_lista_ofertas.py
    """
    from colheita.models import Oferta
    visiveis = Q(aberta_a_todas_em__lte=timezone.now())
    if ong is not None:
        visiveis |= Q(ong_destino=ong)
    ofertas = Oferta.objects.filter(
        visiveis, situacao=SituacaoOferta.ABERTA, colher_ate__gte=date.today(),
    ).select_related('localidade')
    ofertas = [oferta for oferta in ofertas if oferta.saldo > 0]
    if ong is None:
        return ofertas
    for oferta in ofertas:
        oferta.distancia_km = distancia_km(ong.localidade, oferta.localidade)
    ofertas = [o for o in ofertas if limite_km is None or o.distancia_km <= limite_km]
    return sorted(ofertas, key=lambda o: (not o.so_da_ong_destino, not o.urgente, o.distancia_km))


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
    """RF-20, RF-27, RN-01, RN-03, RN-16, E-01, E-04, UC-09 (BL-34, Gabriel em dupla com Jimmie).

    Dentro de transaction.atomic(), trava a oferta com select_for_update(), recalcula o saldo e cria a
    Reserva. Levanta ValidationError se a ONG não está ativa, se a oferta foi cancelada ou venceu
    (as reservas já feitas continuam valendo, RN-18), se a quantidade é <= 0, se passa do saldo
    ("Só restam X kg desta oferta.") ou se tem mais casas decimais do que a unidade aceita. Devolve a
    Reserva; o contato do agricultor e o da ONG passam a aparecer por causa dela (RF-27).
    Testes: colheita/tests/test_reserva.py
    """
    from colheita.models import Oferta, Reserva
    if ong.situacao != SituacaoOng.ATIVA:
        raise ValidationError('Só uma ONG ativa pode reservar ofertas.')
    with transaction.atomic():
        oferta = Oferta.objects.select_for_update().get(pk=oferta.pk)
        if oferta.situacao != SituacaoOferta.ABERTA or oferta.vencida:
            raise ValidationError('Esta oferta não está mais disponível para reserva.')
        if oferta.so_da_ong_destino and oferta.ong_destino_id != ong.pk:
            raise ValidationError('Esta oferta está reservada à ONG de destino nas primeiras 48 h.')
        if quantidade <= 0:
            raise ValidationError('Informe uma quantidade maior que zero.')
        disponivel = saldo(oferta)
        if quantidade > disponivel:
            raise ValidationError(f'Só restam {number_format(disponivel.normalize())} {oferta.unidade} desta oferta.')
        erro_fracao = erro_de_fracao(quantidade, oferta.unidade)
        if erro_fracao:
            raise ValidationError(erro_fracao)
        return Reserva.objects.create(oferta=oferta, ong=ong, quantidade=quantidade)


def reservas_da_ong(ong):
    """RF-27 (BL-34). Reservas da ONG para a Tela 11, das mais novas para as mais antigas, com o
    distancia_km da ONG até a oferta em cada oferta. O contato do agricultor vem junto: a ONG só chega
    aqui porque reservou.
    Testes: colheita/tests/test_tela_reservar.py
    """
    from colheita.models import Reserva
    reservas = list(Reserva.objects.filter(ong=ong).select_related(
        'oferta__localidade', 'oferta__agricultor__usuario'))
    for reserva in reservas:
        reserva.oferta.distancia_km = distancia_km(ong.localidade, reserva.oferta.localidade)
    return reservas


def confirmar_recebimento(reserva, quantidade_recebida):
    """RF-23, RN-16, RN-17, RN-18, E-02, E-03 (BL-35, Gabriel em dupla com Jimmie).

    Dentro de transaction.atomic(), trava a reserva com select_for_update() e devolve a reserva atualizada.
    Levanta ValidationError se a reserva não está ativa, se a quantidade passa da reservada (ou é negativa)
    ou se tem mais casas decimais do que a unidade aceita.
    Maior que 0: situacao = recebida, grava quantidade_recebida e recebida_em (agora); passa a contar no
    painel e a diferença para o reservado não volta ao saldo (ver saldo).
    Igual a 0: situacao = nao_recebida, quantidade_recebida = 0, sem recebida_em; não conta no painel e a
    quantidade volta ao saldo (saldo ignora a não recebida). Em oferta vencida o saldo não importa: ela já
    saiu da lista e a confirmação continua valendo (RN-18).
    Testes: colheita/tests/test_recebimento.py
    """
    from colheita.models import Reserva
    with transaction.atomic():
        reserva = Reserva.objects.select_for_update().select_related('oferta').get(pk=reserva.pk)
        if reserva.situacao != SituacaoReserva.ATIVA:
            raise ValidationError('Esta reserva já foi encerrada.')
        if quantidade_recebida < 0 or quantidade_recebida > reserva.quantidade:
            raise ValidationError(
                f"A quantidade recebida vai de 0 até {number_format(reserva.quantidade.normalize())} {reserva.oferta.unidade}.")
        erro_fracao = erro_de_fracao(quantidade_recebida, reserva.oferta.unidade)
        if erro_fracao:
            raise ValidationError(erro_fracao)
        reserva.quantidade_recebida = quantidade_recebida
        if quantidade_recebida > 0:
            reserva.situacao = SituacaoReserva.RECEBIDA
            reserva.recebida_em = timezone.now()
        else:
            reserva.situacao = SituacaoReserva.NAO_RECEBIDA
        reserva.save(update_fields=['situacao', 'quantidade_recebida', 'recebida_em'])
    return reserva


def cancelar_reserva(reserva, cancelada_por):
    """RF-24, RN-03, RN-18, UC-09, UC-11 (BL-47, Gabriel).

    Dentro de transaction.atomic(), trava a reserva com select_for_update() e devolve a reserva atualizada.
    Levanta ValidationError se a reserva não está ativa (recebida, não recebida ou já cancelada).
    Grava situacao = cancelada e cancelada_por (CanceladaPor: ong, agricultor ou sistema); a quantidade
    volta ao saldo (saldo ignora a cancelada). Quem pode cancelar (a ONG dona da reserva ou o agricultor
    dono da oferta) é conferido pela view. Em oferta vencida a reserva também cancela (RN-18).
    Testes: colheita/tests/test_cancelamentos.py
    """
    from colheita.models import Reserva
    with transaction.atomic():
        reserva = Reserva.objects.select_for_update().select_related('oferta').get(pk=reserva.pk)
        if reserva.situacao != SituacaoReserva.ATIVA:
            raise ValidationError('Só uma reserva ativa pode ser cancelada.')
        reserva.situacao = SituacaoReserva.CANCELADA
        reserva.cancelada_por = cancelada_por
        reserva.save(update_fields=['situacao', 'cancelada_por'])
    return reserva


def cancelar_oferta(oferta):
    """RF-24, RN-03, UC-11 (BL-47, Gabriel).

    Dentro de transaction.atomic(), trava a oferta com select_for_update() e devolve a oferta atualizada.
    Levanta ValidationError se a oferta já está cancelada ou se ainda tem reserva ativa (o agricultor
    cancela a reserva antes). Grava situacao = cancelada: a oferta sai da lista das ONGs. As reservas
    recebidas continuam contando no painel. Quem pode cancelar (o agricultor dono) é conferido pela view.
    Testes: colheita/tests/test_cancelamentos.py
    """
    from colheita.models import Oferta
    with transaction.atomic():
        oferta = Oferta.objects.select_for_update().get(pk=oferta.pk)
        if oferta.situacao == SituacaoOferta.CANCELADA:
            raise ValidationError('Esta oferta já foi cancelada.')
        if oferta.reservas.filter(situacao=SituacaoReserva.ATIVA).exists():
            raise ValidationError('Só é possível cancelar ofertas sem reservas ativas. Cancele as reservas primeiro.')
        oferta.situacao = SituacaoOferta.CANCELADA
        oferta.save(update_fields=['situacao'])
    return oferta


def resumo_recebido(oferta):
    """RF-25, RN-08, RN-09 (BL-36 parte 1, Pedro). O que já foi entregue de uma oferta, para a Minhas ofertas
    (protótipo, Tela 13): "260 un recebidas por 2 ONGs · Renda gerada R$ 208,00".

    Lê oferta.reservas.all(), então funciona igual com o mock de hoje e com o model Reserva da camada 1
    (related_name='reservas'). Na parte 2 da BL-36, a view só troca o mock pela consulta ao banco
    (com prefetch_related('reservas__ong')) e ganha a proteção de perfil (RNF-05).

    Só contam as reservas recebidas. Devolve um dict com:
    - quantidade_recebida: soma de quantidade_recebida (Decimal);
    - ongs: quantas ONGs diferentes receberam;
    - renda: preco_unitario × quantidade_recebida, só em oferta de venda (None em doação).
    Testes: colheita/tests/test_resumo_recebido.py
    """
    recebidas = [r for r in oferta.reservas.all() if r.situacao == SituacaoReserva.RECEBIDA]
    quantidade = sum((r.quantidade_recebida for r in recebidas), Decimal('0'))
    renda = None
    if oferta.destino == Destino.VENDER:
        renda = (quantidade * oferta.preco_unitario).quantize(Decimal('0.01'))
    return {'quantidade_recebida': quantidade, 'ongs': len({r.ong.pk for r in recebidas}), 'renda': renda}
