"""Dados mock do app doacoes (ADR-004). Camada 2: só vira banco se houver tempo."""
from datetime import date
from decimal import Decimal

from core.mocks_util import lista, obj
from ongs.mocks import ONGS

_SOL, _SEMEAR, _MULHERES, _ESPERANCA = ONGS[0], ONGS[1], ONGS[2], ONGS[4]

# Contribuições da Mariana Costa (Tela 14)
CONTRIBUICOES_DA_PESSOA = lista(
    obj(pk=1, tipo='itens', ong=_SOL, necessidade=_SOL.necessidades[0], quantidade=Decimal(10),
        quantidade_confirmada=None, situacao='pendente', criada_em=date(2026, 10, 14), confirmada_em=None),
    obj(pk=2, tipo='dinheiro', ong=_ESPERANCA, necessidade=None, quantidade=Decimal(30),
        quantidade_confirmada=None, situacao='pendente', criada_em=date(2026, 10, 15), confirmada_em=None),
    obj(pk=3, tipo='voluntariado', ong=_SOL, necessidade=_SOL.necessidades[1], quantidade=Decimal(1),
        quantidade_confirmada=Decimal(1), situacao='confirmada', criada_em=date(2026, 10, 5),
        confirmada_em=date(2026, 10, 8)),
    obj(pk=4, tipo='dinheiro', ong=_MULHERES, necessidade=_MULHERES.necessidades[0], quantidade=Decimal(50),
        quantidade_confirmada=Decimal(50), situacao='confirmada', criada_em=date(2026, 9, 28),
        confirmada_em=date(2026, 9, 30)),
    obj(pk=5, tipo='itens', ong=_SEMEAR, necessidade=_SEMEAR.necessidades[0], quantidade=Decimal(5),
        quantidade_confirmada=None, situacao='recusada', criada_em=date(2026, 9, 20), confirmada_em=None),
)

# Pendentes para a Cozinha Solidária Sol Nascente confirmar (Tela 12)
PENDENTES_DA_ONG = lista(
    obj(pk=1, tipo='itens', pessoa=obj(nome_completo='Mariana Costa', telefone='(61) 99812-4433'),
        necessidade=_SOL.necessidades[0], quantidade=Decimal(10), situacao='pendente'),
    obj(pk=6, tipo='voluntariado', pessoa=obj(nome_completo='João Pedro Lima', telefone='(61) 98444-1290'),
        necessidade=_SOL.necessidades[1], quantidade=Decimal(1), situacao='pendente'),
    obj(pk=7, tipo='dinheiro', pessoa=obj(nome_completo='Carlos Souza', telefone='(61) 99100-2030'),
        necessidade=_SOL.necessidades[2], quantidade=Decimal(50), situacao='pendente'),
)
