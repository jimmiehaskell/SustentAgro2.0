from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from contas.choices import TipoConta
from ongs import services
from ongs.choices import SituacaoNecessidade, SituacaoOng, TipoNecessidade, VerificacaoCnpj

# RNF-06: formatos aceitos no upload de imagens (o tamanho é conferido em services.validar_tamanho_da_imagem)
EXTENSOES_DE_IMAGEM = ['jpeg', 'jpg', 'png', 'webp']


class Ods(models.Model):
    """Catálogo fixo de ODS: 1, 2, 4, 5, 8 e 10 (D-14). Mantido pelo administrador."""

    numero = models.PositiveSmallIntegerField('número', unique=True)
    nome = models.CharField(max_length=80)
    cor = models.CharField(max_length=7, help_text='Cor em hexadecimal, por exemplo: #DDA63A.')

    class Meta:
        ordering = ['numero']
        verbose_name = 'ODS'
        verbose_name_plural = 'ODS'

    def __str__(self):
        return f'{self.numero} · {self.nome}'


class Ong(models.Model):
    """Perfil da ONG, ligado a uma conta do tipo ONG (RF-11, RF-12, D-10, D-27, ADR-002).

    Nasce pendente e só aparece nas telas públicas quando fica ativa (RN-01). As ações do admin
    "Aprovar", "Reprovar" e "Desativar" entram no BL-29 e chamam ongs.services.
    """

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ong',
                                   verbose_name='usuário')
    nome = models.CharField(max_length=150, unique=True)
    nome_curto = models.CharField('nome curto', max_length=60, unique=True)
    cnpj = models.CharField('CNPJ', max_length=14, unique=True, help_text='Só os 14 dígitos.')  # validação: BL-29
    slogan = models.CharField('frase de apresentação', max_length=160, blank=True)
    descricao = models.TextField('descrição', blank=True)
    logo = models.ImageField(upload_to='ongs/logos/', blank=True, validators=[
        FileExtensionValidator(EXTENSOES_DE_IMAGEM), services.validar_tamanho_da_imagem])
    capa = models.ImageField('imagem de capa', upload_to='ongs/capas/', blank=True, validators=[
        FileExtensionValidator(EXTENSOES_DE_IMAGEM), services.validar_tamanho_da_imagem])
    telefone = models.CharField(max_length=20)
    email_contato = models.EmailField('e-mail de contato')
    site = models.URLField(blank=True)
    chave_pix = models.CharField('chave Pix', max_length=120, blank=True)
    familias_por_mes = models.PositiveIntegerField('famílias atendidas por mês', default=0)  # RN-10
    aceita_itens = models.BooleanField('aceita itens', default=False)  # P-04
    aceita_dinheiro = models.BooleanField('aceita dinheiro', default=False)
    aceita_voluntariado = models.BooleanField('aceita voluntariado', default=False)
    situacao = models.CharField('situação', max_length=10, choices=SituacaoOng.choices,
                                default=SituacaoOng.PENDENTE)
    motivo_reprovacao = models.TextField('motivo da reprovação', blank=True)
    verificacao_cnpj = models.CharField('verificação do CNPJ', max_length=15, choices=VerificacaoCnpj.choices,
                                        default=VerificacaoCnpj.NAO_CONSULTADO)
    criada_em = models.DateTimeField('criada em', auto_now_add=True)
    aprovada_em = models.DateTimeField('aprovada em', null=True, blank=True)
    localidade = models.ForeignKey('contas.Localidade', on_delete=models.PROTECT, related_name='ongs')
    # Pelo menos 1 ODS: conferido no formulário do perfil (BL-31), porque o ManyToMany só é gravado depois da ONG
    ods = models.ManyToManyField(Ods, related_name='ongs', verbose_name='ODS')

    class Meta:
        verbose_name = 'ONG'
        verbose_name_plural = 'ONGs'

    def __str__(self):
        return self.nome

    def clean(self):
        """Valida a ONG em full_clean() e nos formulários do Django Admin."""
        super().clean()
        # O formulário pode ainda não ter um usuário válido selecionado.
        usuario = getattr(self, 'usuario', None)
        if usuario is not None and usuario.tipo_conta != TipoConta.ONG:
            raise ValidationError({'usuario': 'Só uma conta do tipo ONG pode ter o perfil de ONG.'})


class Necessidade(models.Model):
    """O que a ONG precisa agora (RF-13, RN-02, RN-21). Na camada 1, só a carga de demonstração cria
    necessidades (A-01); a gestão pela ONG entra na camada 2 (BL-41)."""

    ong = models.ForeignKey(Ong, on_delete=models.CASCADE, related_name='necessidades', verbose_name='ONG')
    titulo = models.CharField('título', max_length=120)
    descricao = models.TextField('descrição', blank=True)
    tipo = models.CharField(max_length=12, choices=TipoNecessidade.choices)
    unidade = models.CharField(max_length=30, help_text='Por exemplo: cestas, kg, voluntários, R$.')
    meta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    situacao = models.CharField('situação', max_length=10, choices=SituacaoNecessidade.choices,
                                default=SituacaoNecessidade.ABERTA)
    criada_em = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'{self.titulo} ({self.ong.nome_curto})'

    # Propriedades com os mesmos nomes dos mocks (ADR-004); a regra fica em ongs.services
    @property
    def confirmado(self):
        """RN-02: quanto já foi confirmado pela ONG."""
        return services.confirmado_da_necessidade(self)

    @property
    def percentual(self):
        """RN-21: quanto da meta já foi atingido, de 0 a 100."""
        return services.percentual_da_necessidade(self)
