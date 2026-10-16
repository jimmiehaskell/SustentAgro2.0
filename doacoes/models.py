from django.db import models  # noqa: F401  (usado quando o model abaixo for criado)

# ---------------------------------------------------------------------------------------------
# Camada 2 (BL-42 a BL-45): criar o model abaixo só se houver tempo (project-plan.md §1).
# Uma entidade única para itens, voluntariado e dinheiro (decisão da Fase 4a).
#
# class Contribuicao(models.Model):                      # RF-14 a RF-17, RN-02, RN-07
#     pessoa                 ForeignKey('contas.PerfilPessoa', on_delete=PROTECT, related_name='contribuicoes')
#     ong                    ForeignKey('ongs.Ong', on_delete=PROTECT, related_name='contribuicoes')
#     necessidade            ForeignKey('ongs.Necessidade', null=True, blank=True, on_delete=PROTECT,
#                                       related_name='contribuicoes')  # vazio só em dinheiro livre (D-24)
#     tipo                   CharField(choices=TipoContribuicao.choices)
#     quantidade             DecimalField(max_digits=10, decimal_places=2)   # itens, 1 voluntário ou R$
#     quantidade_confirmada  DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     situacao               CharField(choices=SituacaoContribuicao.choices, default=PENDENTE)
#     criada_em              DateTimeField(auto_now_add=True)
#     confirmada_em          DateTimeField(null=True, blank=True)
# ---------------------------------------------------------------------------------------------
