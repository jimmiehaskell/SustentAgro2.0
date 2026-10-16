"""Listas de valores fixos do app ongs (modelo de dados, página 2)."""
from django.db import models


class SituacaoOng(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    ATIVA = 'ativa', 'Ativa'
    REPROVADA = 'reprovada', 'Reprovada'
    DESATIVADA = 'desativada', 'Desativada'


class VerificacaoCnpj(models.TextChoices):
    NAO_CONSULTADO = 'nao_consultado', 'Não consultado'
    CONFIRMADO = 'confirmado', 'Confirmado'
    NAO_CONFIRMADO = 'nao_confirmado', 'Não confirmado'


class TipoNecessidade(models.TextChoices):
    """Os mesmos valores do tipo de ajuda aceito pela ONG (A-04)."""
    ITENS = 'itens', 'Itens'
    DINHEIRO = 'dinheiro', 'Dinheiro'
    VOLUNTARIADO = 'voluntariado', 'Voluntariado'


class SituacaoNecessidade(models.TextChoices):
    ABERTA = 'aberta', 'Aberta'
    ATENDIDA = 'atendida', 'Atendida'
    ENCERRADA = 'encerrada', 'Encerrada'
