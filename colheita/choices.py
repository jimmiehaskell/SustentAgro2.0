"""Listas de valores fixos do app colheita (modelo de dados, página 2)."""
from django.db import models


class Categoria(models.TextChoices):
    HORTALICAS = 'hortalicas', 'Hortaliças'
    FRUTAS = 'frutas', 'Frutas'
    RAIZES_TUBERCULOS = 'raizes_tuberculos', 'Raízes e tubérculos'
    GRAOS = 'graos', 'Grãos'
    OUTROS = 'outros', 'Outros'


class Unidade(models.TextChoices):
    KG = 'kg', 'kg'
    UN = 'un', 'un'


class Estado(models.TextChoices):
    EXCEDENTE = 'excedente', 'Excedente'
    FORA_DO_PADRAO = 'fora_do_padrao', 'Fora do padrão'


class Destino(models.TextChoices):
    DOAR = 'doar', 'Doar'
    VENDER = 'vender', 'Vender'


class Transporte(models.TextChoices):
    ONG_BUSCA = 'ong_busca', 'A ONG busca'
    AGRICULTOR_LEVA = 'agricultor_leva', 'O agricultor leva'


class SituacaoOferta(models.TextChoices):
    ABERTA = 'aberta', 'Aberta'
    CANCELADA = 'cancelada', 'Cancelada'


class SituacaoReserva(models.TextChoices):
    ATIVA = 'ativa', 'Ativa'
    RECEBIDA = 'recebida', 'Recebida'
    NAO_RECEBIDA = 'nao_recebida', 'Não recebida'
    CANCELADA = 'cancelada', 'Cancelada'


class CanceladaPor(models.TextChoices):
    ONG = 'ong', 'ONG'
    AGRICULTOR = 'agricultor', 'Agricultor'
    SISTEMA = 'sistema', 'Sistema'
