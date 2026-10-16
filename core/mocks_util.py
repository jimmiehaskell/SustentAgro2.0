"""Ferramentas para os dados mock (ADR-004).

Os mocks precisam se comportar como objetos do Django no template, para que a troca de mock
para banco não mude o template. Por isso:

- use ``obj(...)`` em vez de dicionário, para acessar ``ong.nome`` igual a um model;
- use ``lista(...)`` para relacionamentos, para o template poder chamar ``ong.ods.all``
  igual a um ManyToMany ou a um related_name de verdade.
"""
from types import SimpleNamespace


class ListaMock(list):
    def all(self):
        return self

    def count(self):
        return len(self)

    def exists(self):
        return bool(self)


def obj(**campos):
    return SimpleNamespace(**campos)


def lista(*itens):
    return ListaMock(itens)
