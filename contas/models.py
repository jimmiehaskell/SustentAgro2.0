from django.contrib.auth.models import AbstractUser
from django.db import models

from contas.choices import TipoConta


class Usuario(AbstractUser):
    """Conta de login (ADR-002). O perfil fica em PerfilPessoa ou em ongs.Ong."""
    tipo_conta = models.CharField('tipo de conta', max_length=10, choices=TipoConta.choices,
                                  default=TipoConta.PESSOA)

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'


# ---------------------------------------------------------------------------------------------
# BL-24 (Vinicius): criar os models abaixo, exatamente com estes nomes (modelo de dados, Anexo B).
#
# class Localidade(models.Model):                       # RF-33, P-06, A-05
#     nome       CharField(max_length=80, unique=True)
#     uf         CharField(max_length=2, choices=UF.choices)
#     latitude   DecimalField(max_digits=9, decimal_places=6)
#     longitude  DecimalField(max_digits=9, decimal_places=6)
#     Meta: ordering = ['nome']
#
# class PerfilPessoa(models.Model):                     # RN-12, D-15
#     usuario        OneToOneField(Usuario, on_delete=CASCADE, related_name='perfil_pessoa')
#     nome_completo  CharField(max_length=150)
#     telefone       CharField(max_length=20, blank=True)
#     eh_doador      BooleanField(default=False)
#     eh_agricultor  BooleanField(default=False)
#     localidade     ForeignKey(Localidade, null=True, blank=True, on_delete=PROTECT,
#                               related_name='perfis')  # obrigatória para agricultor
#
# Os testes de tests/test_perfil.py estão marcados com skip: remova o skip ao implementar.
# ---------------------------------------------------------------------------------------------
