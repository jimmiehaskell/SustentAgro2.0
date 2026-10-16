"""Listas de valores fixos do app contas (modelo de dados, página 2)."""
from django.db import models


class TipoConta(models.TextChoices):
    PESSOA = 'pessoa', 'Pessoa'
    ONG = 'ong', 'ONG'


class UF(models.TextChoices):
    DF = 'DF', 'DF'
    GO = 'GO', 'GO'
    MG = 'MG', 'MG'
