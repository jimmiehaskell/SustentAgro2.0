"""Regras de negócio da Colheita Solidária (ADR-001, ADR-003).

Toda função que muda dados levanta django.core.exceptions.ValidationError com uma mensagem em
português quando a regra não é atendida; a view mostra essa mensagem para a pessoa.
"""


def distancia_km(origem, destino):
    """RN-15 (BL-33, Gabriel). Distância em linha reta (fórmula de haversine) entre duas localidades,
    usando latitude e longitude. Mesma localidade = 0. Devolve float arredondado para 1 casa.
    Testes: colheita/tests/test_distancia.py
    """
    raise NotImplementedError('BL-33')


def saldo(oferta):
    """RN-03 (BL-26). Quantidade publicada menos a soma das reservas ativas e recebidas.
    Reservas canceladas e não recebidas não contam. Nunca negativo.
    """
    raise NotImplementedError('BL-26')


def validar_oferta(oferta):
    """RN-13, RN-16, UC-08 (BL-32, Gabriel). Levanta ValidationError se:
    - destino = vender sem preço, ou destino = doar com preço;
    - unidade = un com quantidade fracionada;
    - colher_ate no passado.
    """
    raise NotImplementedError('BL-32')


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
