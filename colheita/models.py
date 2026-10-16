from django.db import models  # noqa: F401  (usado quando os models abaixo forem criados)

# ---------------------------------------------------------------------------------------------
# BL-26 (Gabriel, com Jimmie): criar os models abaixo, exatamente com estes nomes (Anexo B).
# Depende de contas.PerfilPessoa, contas.Localidade e ongs.Ong. Use os choices de colheita/choices.py.
#
# class Oferta(models.Model):                            # RF-18, RN-04, RN-05, RN-13, RN-16
#     agricultor         ForeignKey('contas.PerfilPessoa', on_delete=PROTECT, related_name='ofertas')
#     categoria          CharField(choices=Categoria.choices)
#     produto            CharField(max_length=80)
#     quantidade         DecimalField(max_digits=10, decimal_places=1)   # un: só inteiros (RN-16)
#     unidade            CharField(choices=Unidade.choices)
#     colher_ate         DateField()                                      # não pode estar no passado
#     localidade         ForeignKey('contas.Localidade', on_delete=PROTECT, related_name='ofertas')
#     estado             CharField(choices=Estado.choices)
#     destino            CharField(choices=Destino.choices)
#     preco_unitario     DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # RN-13
#     local_retirada     CharField(max_length=200)
#     transporte         CharField(choices=Transporte.choices)
#     situacao           CharField(choices=SituacaoOferta.choices, default=ABERTA)
#     ong_destino        ForeignKey('ongs.Ong', null=True, blank=True, on_delete=SET_NULL,
#                                   related_name='ofertas_direcionadas')
#     criada_em          DateTimeField(auto_now_add=True)
#     aberta_a_todas_em  DateTimeField()      # = criada_em, ou criada_em + 48 h se tiver ong_destino
#     Propriedades calculadas (mesmo nome dos mocks): saldo, urgente, vencida.
#     distancia_km é calculada em relação à ONG que está vendo (services.distancia_km).
#
# class Reserva(models.Model):                           # RF-20, RF-23, RN-03, RN-17
#     oferta               ForeignKey(Oferta, on_delete=PROTECT, related_name='reservas')
#     ong                  ForeignKey('ongs.Ong', on_delete=PROTECT, related_name='reservas')
#     quantidade           DecimalField(max_digits=10, decimal_places=1)
#     situacao             CharField(choices=SituacaoReserva.choices, default=ATIVA)
#     quantidade_recebida  DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
#     recebida_em          DateTimeField(null=True, blank=True)
#     cancelada_por        CharField(choices=CanceladaPor.choices, blank=True)
#     criada_em            DateTimeField(auto_now_add=True)
#
# Regras de negócio NÃO ficam aqui nem na view: ficam em colheita/services.py (ADR-001).
# ---------------------------------------------------------------------------------------------
