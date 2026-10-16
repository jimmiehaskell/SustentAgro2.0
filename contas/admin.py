from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contas.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_conta', 'is_staff')
    list_filter = ('tipo_conta', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (('Perfil', {'fields': ('tipo_conta',)}),)
