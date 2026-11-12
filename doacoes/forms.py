"""Entrada para promessa de itens e inscrição (BL-42)."""
from django import forms


class PromessaItensForm(forms.Form):
    necessidade = forms.IntegerField(min_value=1)
    quantidade = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class InscricaoVoluntariadoForm(forms.Form):
    necessidade = forms.IntegerField(min_value=1)
