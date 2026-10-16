"""Regras de negócio do app ongs (ADR-001). Views e ações do admin só chamam estas funções."""


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
    raise NotImplementedError('BL-29')


def reprovar_ong(ong, motivo):
    """RN-14, RN-20 (BL-29, Júlia): situacao = reprovada e grava o motivo, que a ONG vê ao entrar."""
    raise NotImplementedError('BL-29')


def desativar_ong(ong):
    """RN-14, RN-19, E-05 (BL-29, Júlia): situacao = desativada e cancela as reservas ativas da ONG
    (cancelada_por = sistema), devolvendo as quantidades ao saldo das ofertas."""
    raise NotImplementedError('BL-29')
