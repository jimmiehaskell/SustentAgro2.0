from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from contas.choices import TipoConta, UF


class Usuario(AbstractUser):
    """Conta de login (ADR-002). O perfil fica em PerfilPessoa ou em ongs.Ong."""
    tipo_conta = models.CharField('tipo de conta', max_length=10, choices=TipoConta.choices,
                                  default=TipoConta.PESSOA)

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'


class Localidade(models.Model):
    """Localidade mantida pelo administrador (RF-33, A-05)."""

    nome = models.CharField(max_length=80, unique=True)
    uf = models.CharField(max_length=2, choices=UF.choices)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} / {self.uf}'


class PerfilPessoa(models.Model):
    """Perfis de doador e agricultor na mesma conta (RN-12, ADR-002)."""

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='perfil_pessoa')
    nome_completo = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20, blank=True)
    eh_doador = models.BooleanField('doador(a) ou voluntário(a)', default=False)
    eh_agricultor = models.BooleanField('agricultor(a)', default=False)
    localidade = models.ForeignKey(
        Localidade, null=True, blank=True, on_delete=models.PROTECT,
        related_name='perfis')

    class Meta:
        verbose_name = 'perfil de pessoa'
        verbose_name_plural = 'perfis de pessoa'

    def __str__(self):
        return self.nome_completo

    def clean(self):
        """Valida o perfil em full_clean() e nos formulários do Django Admin."""
        super().clean()
        erros = {}
        # O formulário pode ainda não ter um usuário válido selecionado.
        usuario = getattr(self, 'usuario', None)
        if usuario is not None and usuario.tipo_conta == TipoConta.ONG:
            erros['usuario'] = 'Uma conta de ONG não pode possuir perfil de pessoa.'
        if self.eh_agricultor and self.localidade_id is None:
            erros['localidade'] = 'Informe a localidade do agricultor.'
        if erros:
            raise ValidationError(erros)
