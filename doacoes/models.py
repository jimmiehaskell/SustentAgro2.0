from django.db import models

from doacoes.choices import SituacaoContribuicao, TipoContribuicao


class Contribuicao(models.Model):
    """Promessa ou inscrição; só a confirmação pela ONG conta no progresso (RN-02)."""

    pessoa = models.ForeignKey('contas.PerfilPessoa', on_delete=models.PROTECT, related_name='contribuicoes')
    ong = models.ForeignKey('ongs.Ong', on_delete=models.PROTECT, related_name='contribuicoes')
    necessidade = models.ForeignKey('ongs.Necessidade', null=True, blank=True, on_delete=models.PROTECT,
                                    related_name='contribuicoes')
    tipo = models.CharField(max_length=12, choices=TipoContribuicao.choices)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_confirmada = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    situacao = models.CharField(max_length=10, choices=SituacaoContribuicao.choices,
                                default=SituacaoContribuicao.PENDENTE)
    criada_em = models.DateTimeField(auto_now_add=True)
    confirmada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'contribuição'
        verbose_name_plural = 'contribuições'

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.pessoa} para {self.ong}'
