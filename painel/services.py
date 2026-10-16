"""Cálculos do painel de impacto (BL-37, Pedro). Só lê dados; nunca grava."""


def indicadores():
    """RF-29. Devolve um objeto (ou dict) com:
    - kg_salvos: soma de quantidade_recebida das reservas recebidas de ofertas em kg (RN-08, P-01);
    - familias_atendidas: soma de familias_por_mes das ONGs ativas (RN-10);
    - renda_gerada: soma de preco_unitario × quantidade_recebida das ofertas de venda recebidas (RN-09);
    - ongs_ativas: quantidade de ONGs com situacao = ativa (RN-11).
    Testes: painel/tests/test_indicadores.py
    """
    raise NotImplementedError('BL-37')


def kg_por_mes():
    """RF-30, RN-23, E-09. Lista de (mês, kg) agrupada pela data de recebida_em, no fuso de Brasília."""
    raise NotImplementedError('BL-37')


def fatia_por_ods():
    """RF-31, RN-07, E-10. Lista de (ods, percentual). Cada ação confirmada conta uma vez para cada ODS da
    ONG que a recebeu; o percentual de um ODS é a contagem dele dividida pela soma das contagens.
    Com só a camada 1 pronta, as ações são as reservas recebidas."""
    raise NotImplementedError('BL-37')
