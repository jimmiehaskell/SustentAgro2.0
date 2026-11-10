from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contas.models import Localidade, PerfilPessoa, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_conta', 'is_staff')
    list_filter = ('tipo_conta', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (('Perfil', {'fields': ('tipo_conta',)}),)


@admin.register(Localidade)
class LocalidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf', 'latitude', 'longitude')
    search_fields = ('nome',)
    list_filter = ('uf',)


@admin.register(PerfilPessoa)
class PerfilPessoaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'usuario', 'eh_doador', 'eh_agricultor', 'localidade')
    search_fields = ('nome_completo', 'usuario__username', 'telefone')
    list_filter = ('eh_doador', 'eh_agricultor', 'localidade')
    list_select_related = ('usuario', 'localidade')
