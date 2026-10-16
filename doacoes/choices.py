"""Listas de valores fixos do app doacoes (modelo de dados, página 2)."""
from django.db import models


class TipoContribuicao(models.TextChoices):
    ITENS = 'itens', 'Itens'
    VOLUNTARIADO = 'voluntariado', 'Voluntariado'
    DINHEIRO = 'dinheiro', 'Dinheiro'


class SituacaoContribuicao(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    CONFIRMADA = 'confirmada', 'Confirmada'
    RECUSADA = 'recusada', 'Recusada'
    CANCELADA = 'cancelada', 'Cancelada'
