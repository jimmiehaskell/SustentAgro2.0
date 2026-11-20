"""Criação transacional de conta e perfil (BL-28, RF-07)."""
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from contas.choices import TipoConta
from ongs.choices import SituacaoOng


@transaction.atomic
def cadastrar_usuario(formulario_conta, formulario_perfil):
    """Grava apenas formulários válidos; qualquer falha desfaz todo o cadastro."""
    from contas.forms import OngCadastroForm

    if not formulario_conta.is_valid() or not formulario_perfil.is_valid():
        raise ValidationError('Confira os dados do cadastro.')
    ong = isinstance(formulario_perfil, OngCadastroForm)
    usuario = formulario_conta.save(commit=False)
    usuario.tipo_conta = TipoConta.ONG if ong else TipoConta.PESSOA
    usuario.email = formulario_perfil.cleaned_data['email_contato' if ong else 'email']
    try:
        validate_password(formulario_conta.cleaned_data['password1'], usuario)
    except ValidationError as erro:
        formulario_conta.add_error('password1', erro)
        raise
    usuario.full_clean()
    usuario.save()
    perfil = formulario_perfil.save(commit=False)
    perfil.usuario = usuario
    if ong:
        perfil.situacao = SituacaoOng.PENDENTE
    perfil.full_clean()
    perfil.save()
    formulario_perfil.save_m2m()
    return usuario
