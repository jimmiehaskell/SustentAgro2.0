from django import forms

from ongs.models import Ong


class PerfilOngForm(forms.ModelForm):
    """Perfil público da ONG (BL-31). RF-12. Nome, CNPJ e situação ficam fora: só o administrador os altera."""

    class Meta:
        model = Ong
        fields = [
            'slogan', 'descricao', 'logo', 'capa', 'ods',
            'aceita_itens', 'aceita_dinheiro', 'aceita_voluntariado',
            'localidade', 'telefone', 'email_contato', 'site',
            'chave_pix', 'familias_por_mes',
                ]
        widgets = {'ods': forms.CheckboxSelectMultiple}