"""Regras de doação e voluntariado (camada 2, BL-42 a BL-45). Só se houver tempo."""


def registrar_contribuicao(pessoa, ong, tipo, quantidade, necessidade=None):
    """RF-14, RF-15, RF-17 (BL-42, BL-43). Cria a contribuição pendente. Necessidade vazia só para
    dinheiro (doação livre, D-24). Necessidade atendida não aceita novas promessas (RN-21)."""
    raise NotImplementedError('BL-42')


def confirmar_contribuicao(contribuicao, quantidade_confirmada):
    """RF-16, RN-02 (BL-44). A barra da necessidade só avança com o que a ONG confirmou."""
    raise NotImplementedError('BL-44')


def recusar_contribuicao(contribuicao):
    """RF-16 (BL-44). situacao = recusada; a barra não muda."""
    raise NotImplementedError('BL-44')


def cancelar_contribuicao(contribuicao):
    """RF-26, P-07 (BL-45). Só pendente; situacao = cancelada."""
    raise NotImplementedError('BL-45')
