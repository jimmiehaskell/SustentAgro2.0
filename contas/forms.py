"""Formulários de cadastro real (BL-28)."""
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm

from contas.models import PerfilPessoa, Usuario
from ongs.models import Ong


def aplicar_estilo(formulario):
    for campo in formulario.fields.values():
        if isinstance(campo.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            classe = 'form-check-input'
        elif isinstance(campo.widget, forms.Select):
            classe = 'form-select'
        else:
            classe = 'form-control'
        campo.widget.attrs['class'] = classe


class ContaCadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilo(self)


class PessoaCadastroForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = PerfilPessoa
        fields = ('nome_completo', 'email', 'telefone', 'localidade')
        labels = {'nome_completo': 'Nome completo'}

    def __init__(self, *args, agricultor=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.eh_agricultor = agricultor
        self.instance.eh_doador = not agricultor
        self.fields['localidade'].required = agricultor
        if not agricultor:
            self.fields['localidade'].label = 'Localidade (opcional)'
        aplicar_estilo(self)


class OngCadastroForm(forms.ModelForm):
    cnpj = forms.CharField(label='CNPJ', max_length=18,
                           help_text='Informe os 14 dígitos, com ou sem pontuação.')

    class Meta:
        model = Ong
        fields = ('nome', 'nome_curto', 'cnpj', 'email_contato', 'telefone', 'localidade',
                  'ods', 'aceita_itens', 'aceita_dinheiro', 'aceita_voluntariado')
        labels = {'nome': 'Nome da ONG', 'ods': 'Causas (ODS)'}
        widgets = {'ods': forms.CheckboxSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilo(self)

    def clean_cnpj(self):
        # Ong.clean() reutiliza a validação da BL-29 após a normalização.
        return re.sub(r'[.\-/\s]', '', self.cleaned_data['cnpj'])
