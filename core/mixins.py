"""Mixins de perfil (BL-05, ADR-002, RNF-05).

Use em toda view da área logada, antes da classe da view:

    class PublicarOfertaView(AgricultorRequeridoMixin, CreateView):
        ...

Quem não está logado vai para o login; quem está logado com outro perfil recebe 403.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from core.perfis import perfil_da_requisicao


class PerfilRequeridoMixin(LoginRequiredMixin):
    perfis_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if perfil_da_requisicao(request) not in self.perfis_permitidos:
            raise PermissionDenied('Esta página não está disponível para o seu perfil.')
        return super().dispatch(request, *args, **kwargs)


class DoadorRequeridoMixin(PerfilRequeridoMixin):
    """Pessoa com perfil de doador/voluntário (contas de pessoa)."""
    perfis_permitidos = ('pessoa', 'agricultor')


class AgricultorRequeridoMixin(PerfilRequeridoMixin):
    perfis_permitidos = ('agricultor',)


class OngRequeridaMixin(PerfilRequeridoMixin):
    """Qualquer ONG, inclusive pendente ou reprovada: só para a "Minha conta" (RN-20)."""
    perfis_permitidos = ('ong', 'ong-pendente', 'ong-reprovada')


class OngAtivaRequeridaMixin(PerfilRequeridoMixin):
    """Só ONG aprovada e não desativada: reservar, criar necessidade, confirmar (RN-01)."""
    perfis_permitidos = ('ong',)
