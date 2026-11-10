"""Models da Colheita Solidária (BL-26, modelo de dados, Anexo B).

Regras de negócio NÃO ficam aqui nem na view: ficam em colheita/services.py (ADR-001). O clean() dos
models só chama os serviços, para o admin e os formulários validarem do mesmo jeito.
"""
from datetime import date, timedelta

from django.db import models
from django.utils import timezone

from colheita import services
from colheita.choices import (CanceladaPor, Categoria, Destino, Estado, SituacaoOferta, SituacaoReserva,
                              Transporte, Unidade)

PRAZO_ONG_DESTINO = timedelta(hours=48)  # RN-04
PRAZO_URGENTE = timedelta(hours=48)      # RF-22


class Oferta(models.Model):
    """RF-18, RN-04, RN-05, RN-13, RN-16."""
    agricultor = models.ForeignKey('contas.PerfilPessoa', on_delete=models.PROTECT, related_name='ofertas')
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    produto = models.CharField(max_length=80)
    quantidade = models.DecimalField(max_digits=10, decimal_places=1)  # un: só inteiros (RN-16)
    unidade = models.CharField(max_length=2, choices=Unidade.choices)
    colher_ate = models.DateField('colher até')
    localidade = models.ForeignKey('contas.Localidade', on_delete=models.PROTECT, related_name='ofertas')
    estado = models.CharField(max_length=20, choices=Estado.choices)
    destino = models.CharField(max_length=10, choices=Destino.choices)
    preco_unitario = models.DecimalField('preço unitário', max_digits=10, decimal_places=2, null=True,
                                         blank=True)  # RN-13
    local_retirada = models.CharField('local de retirada', max_length=200)
    transporte = models.CharField(max_length=20, choices=Transporte.choices)
    situacao = models.CharField('situação', max_length=10, choices=SituacaoOferta.choices,
                                default=SituacaoOferta.ABERTA)
    ong_destino = models.ForeignKey('ongs.Ong', null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='ofertas_direcionadas', verbose_name='ONG de destino')
    criada_em = models.DateTimeField('criada em', auto_now_add=True)
    # Em branco no formulário: o save() preenche (RN-04)
    aberta_a_todas_em = models.DateTimeField('aberta a todas em', blank=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'{self.produto} · {self.quantidade:g} {self.unidade}'

    def clean(self):
        # A data no passado só é recusada ao publicar: uma oferta antiga continua editável no admin
        services.validar_oferta(self, checar_data=self._state.adding)

    def save(self, *args, **kwargs):
        if self.aberta_a_todas_em is None:
            # RN-04: com ONG de destino, só ela vê a oferta nas primeiras 48 h
            self.aberta_a_todas_em = timezone.now() + (PRAZO_ONG_DESTINO if self.ong_destino_id else timedelta())
        super().save(*args, **kwargs)

    # Propriedades calculadas, com os mesmos nomes dos mocks (ADR-004)
    @property
    def saldo(self):
        return services.saldo(self)

    @property
    def vencida(self):
        return self.colher_ate < date.today()

    @property
    def urgente(self):
        """RF-22: aberta, com saldo e aberta a todas há mais de 48 h."""
        return (self.situacao == SituacaoOferta.ABERTA and not self.vencida
                and timezone.now() - self.aberta_a_todas_em > PRAZO_URGENTE and self.saldo > 0)


class Reserva(models.Model):
    """RF-20, RF-23, RN-03, RN-17."""
    oferta = models.ForeignKey(Oferta, on_delete=models.PROTECT, related_name='reservas')
    ong = models.ForeignKey('ongs.Ong', on_delete=models.PROTECT, related_name='reservas', verbose_name='ONG')
    quantidade = models.DecimalField(max_digits=10, decimal_places=1)
    situacao = models.CharField('situação', max_length=15, choices=SituacaoReserva.choices,
                                default=SituacaoReserva.ATIVA)
    quantidade_recebida = models.DecimalField('quantidade recebida', max_digits=10, decimal_places=1,
                                              null=True, blank=True)
    recebida_em = models.DateTimeField('recebida em', null=True, blank=True)
    cancelada_por = models.CharField('cancelada por', max_length=10, choices=CanceladaPor.choices, blank=True)
    criada_em = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'{self.oferta.produto} · {self.quantidade:g} {self.oferta.unidade} · {self.ong}'

    def clean(self):
        services.validar_quantidade_da_reserva(self)
