from django.db import models  # noqa: F401  (usado quando os models abaixo forem criados)
from decimal import Decimal
from django.conf import settings
from .choices import (SituacaoNecessidade,SituacaoOng,TipoNecessidade,VerificacaoCnpj)


class Ods(models.Model):                               # catálogo fixo: 1, 2, 4, 5, 8 e 10 (D-14)
     numero=models.PositiveSmallIntegerField(unique=True)
     nome=models.CharField(max_length=80)
     cor=models.CharField(max_length=7)                    # hexadecimal, ex.: '#DDA63A'

class Meta:
    ordering = ['numero']
    verbose_name = 'ODS'
    verbose_name_plural = 'ODS'

    def __str__(self):
        return f'ODS {self.numero} - {self.nome}'

class Ong(models.Model):                               # RF-11, RF-12, D-10, D-27
     usuario=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='ong')
     nome=models.CharField(max_length=150, unique=True)
     nome_curto=models.CharField(max_length=60, unique=True)
     cnpj=models.CharField(max_length=14, unique=True)        # só dígitos; validar (RF-10)
     slogan=models.CharField(max_length=160, blank=True)
     descricao=models.TextField(blank=True)
     logo=models.ImageField(upload_to=..., blank=True)        # jpeg, jpg, png, webp; até 10 MB (RNF-06)
     capa=models.ImageField(upload_to=..., blank=True)
     telefone=models.CharField(max_length=20)
     email_contato=models.EmailField()
     site=models.URLField(blank=True)
     chave_pix=models.CharField(max_length=120, blank=True)
     familias_por_mes=models.PositiveIntegerField(default=0)              # RN-10
     aceita_itens=models.BooleanField(default=False)                  # P-04
     aceita_dinheiro=models.BooleanField(default=False)
     aceita_voluntariado=models.BooleanField(default=False)
     situacao=models.CharField(choices=SituacaoOng.choices, default=PENDENTE)
     motivo_reprovacao=models.TextField(blank=True)
     verificacao_cnpj=models.CharField(choices=VerificacaoCnpj.choices, default=NAO_CONSULTADO)
     criada_em=models.DateTimeField(auto_now_add=True)
     aprovada_em=models.DateTimeField(null=True, blank=True)
     localidade=models.ForeignKey('contas.Localidade', on_delete=PROTECT, related_name='ongs')
     ods=models.ManyToManyField(Ods, related_name='ongs')    # pelo menos 1 (validar no form)

class Necessidade(models.Model):                       # RF-13, RN-02, RN-21
     ong=models.ForeignKey(Ong, on_delete=CASCADE, related_name='necessidades')
     titulo=models.CharField(max_length=120)
     descricao=models.TextField(blank=True)
     tipo=models.CharField(choices=TipoNecessidade.choices)
     unidade=models.CharField(max_length=30)                # ex.: 'cestas', 'kg', 'voluntários', 'R$'
     meta=models.DecimalField(max_digits=10, decimal_places=2)
     situacao=models.CharField(choices=SituacaoNecessidade.choices, default=ABERTA)
     criada_em=models.DateTimeField(auto_now_add=True)
     meta = models.DecimalField(max_digits=10, decimal_places=2)
class Meta:
        ordering = ['-criada_em']
        verbose_name_plural = 'necessidades'    

def __str__(self):
    return self.titulo

@property
def confirmado(self):
    # RN-02: só conta o que a ONG confirmou. Ainda não existe model de
    # doações/inscrições; quando existir, somar aqui os valores confirmados.
    return Decimal('0')

@property
def percentual(self):
    if not self.meta:
        return 0
    return min(100, int(self.confirmado * 100 / self.meta))