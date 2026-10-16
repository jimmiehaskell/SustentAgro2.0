"""BL-05: mixins de perfil (ADR-002, RNF-05, RN-01, RN-20)."""
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views import View

from core.mixins import AgricultorRequeridoMixin, OngAtivaRequeridaMixin, OngRequeridaMixin
from core.tests.fabricas import criar_usuario


def _view(mixin):
    class Tela(mixin, View):
        def get(self, request):
            return HttpResponse('ok')
    return Tela.as_view()


class MixinsTest(TestCase):
    def setUp(self):
        self.fabrica = RequestFactory()

    def _get(self, mixin, usuario=None):
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.sessions.backends.db import SessionStore
        request = self.fabrica.get('/qualquer/')
        request.user = usuario or AnonymousUser()
        request.session = SessionStore()
        return _view(mixin)(request)

    def test_visitante_vai_para_o_login(self):
        resposta = self._get(AgricultorRequeridoMixin)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/conta/entrar/', resposta['Location'])

    def test_pessoa_sem_perfil_de_agricultor_recebe_403(self):
        from django.core.exceptions import PermissionDenied
        with self.assertRaises(PermissionDenied):
            self._get(AgricultorRequeridoMixin, criar_usuario('pessoa'))

    def test_ong_sem_aprovacao_entra_na_minha_conta(self):
        # Sem o model Ong (BL-25), toda conta de ONG conta como pendente (RN-20)
        self.assertEqual(self._get(OngRequeridaMixin, criar_usuario('ong')).status_code, 200)

    def test_ong_pendente_nao_reserva(self):
        from django.core.exceptions import PermissionDenied
        with self.assertRaises(PermissionDenied):
            self._get(OngAtivaRequeridaMixin, criar_usuario('ong'))
