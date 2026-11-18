"""BL-31 (Júlia): edição do perfil da ONG em /minha-ong/. RF-12, RNF-05, RNF-06, RN-20."""
import io
import tempfile

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core.tests.fabricas import criar_ong
from ongs.choices import SituacaoOng


def _imagem(nome='logo.png', formato='PNG'):
    buf = io.BytesIO()
    Image.new('RGB', (4, 4)).save(buf, formato)
    return SimpleUploadedFile(nome, buf.getvalue())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PerfilOngTests(TestCase):
    def setUp(self):
        # ong_a pendente: prova que ONG pendente edita o perfil (RN-20)
        self.ong_a = criar_ong(situacao=SituacaoOng.PENDENTE, ods=(1,))
        self.ong_b = criar_ong(ods=(1,))
        self.client.force_login(self.ong_a.usuario)
        self.url = reverse('ongs:minha_ong')

    def _post(self, follow=False, **extra):
        dados = {
            'descricao': 'Nova descrição',
            'telefone': '61999999999',
            'email_contato': 'contato@exemplo.org',
            'localidade': self.ong_a.localidade_id,
            'ods': [self.ong_a.ods.first().pk],
            'familias_por_mes': 10,
            **extra,
        }
        return self.client.post(self.url, dados, follow=follow)

    def test_edita_o_proprio_perfil(self):
        self._post(descricao='Texto novo', chave_pix='ong@pix.com')
        self.ong_a.refresh_from_db()
        self.assertEqual(self.ong_a.descricao, 'Texto novo')
        self.assertEqual(self.ong_a.chave_pix, 'ong@pix.com')

    def test_mensagem_de_sucesso_aparece_uma_vez(self):
        resposta = self._post(follow=True, descricao='Texto novo')
        self.assertContains(resposta, 'Perfil atualizado.', count=1)

    def test_nao_altera_outra_ong(self):
        antes = self.ong_b.descricao
        self._post(descricao='Invasão', id=self.ong_b.pk)
        self.ong_b.refresh_from_db()
        self.assertEqual(self.ong_b.descricao, antes)

    def test_nao_permite_trocar_situacao_nem_cnpj(self):
        cnpj, situacao = self.ong_a.cnpj, self.ong_a.situacao
        self._post(situacao=SituacaoOng.ATIVA, cnpj='00000000000000')
        self.ong_a.refresh_from_db()
        self.assertEqual(self.ong_a.cnpj, cnpj)
        self.assertEqual(self.ong_a.situacao, situacao)

    def test_exige_ao_menos_um_ods(self):
        resposta = self._post(ods=[])
        self.assertIn('ods', resposta.context['form'].errors)

    def test_aceita_png_no_logo(self):
        resposta = self._post(logo=_imagem())
        self.assertEqual(resposta.status_code, 302)

    def test_rejeita_extensao_invalida(self):
        resposta = self._post(logo=_imagem('logo.gif', 'GIF'))
        self.assertIn('logo', resposta.context['form'].errors)
