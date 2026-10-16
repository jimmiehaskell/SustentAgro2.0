from django.db import models  # noqa: F401  (usado quando os models abaixo forem criados)

# ---------------------------------------------------------------------------------------------
# BL-25 (Júlia): criar os models abaixo, exatamente com estes nomes (modelo de dados, Anexo B).
# Depende de contas.Localidade (BL-24). Use os choices de ongs/choices.py.
#
# class Ods(models.Model):                               # catálogo fixo: 1, 2, 4, 5, 8 e 10 (D-14)
#     numero  PositiveSmallIntegerField(unique=True)
#     nome    CharField(max_length=80)
#     cor     CharField(max_length=7)                    # hexadecimal, ex.: '#DDA63A'
#     Meta: ordering = ['numero']
#
# class Ong(models.Model):                               # RF-11, RF-12, D-10, D-27
#     usuario              OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='ong')
#     nome                 CharField(max_length=150, unique=True)
#     nome_curto           CharField(max_length=60, unique=True)
#     cnpj                 CharField(max_length=14, unique=True)        # só dígitos; validar (RF-10)
#     slogan               CharField(max_length=160, blank=True)
#     descricao            TextField(blank=True)
#     logo                 ImageField(upload_to=..., blank=True)        # jpeg, jpg, png, webp; até 10 MB (RNF-06)
#     capa                 ImageField(upload_to=..., blank=True)
#     telefone             CharField(max_length=20)
#     email_contato        EmailField()
#     site                 URLField(blank=True)
#     chave_pix            CharField(max_length=120, blank=True)
#     familias_por_mes     PositiveIntegerField(default=0)              # RN-10
#     aceita_itens         BooleanField(default=False)                  # P-04
#     aceita_dinheiro      BooleanField(default=False)
#     aceita_voluntariado  BooleanField(default=False)
#     situacao             CharField(choices=SituacaoOng.choices, default=PENDENTE)
#     motivo_reprovacao    TextField(blank=True)
#     verificacao_cnpj     CharField(choices=VerificacaoCnpj.choices, default=NAO_CONSULTADO)
#     criada_em            DateTimeField(auto_now_add=True)
#     aprovada_em          DateTimeField(null=True, blank=True)
#     localidade           ForeignKey('contas.Localidade', on_delete=PROTECT, related_name='ongs')
#     ods                  ManyToManyField(Ods, related_name='ongs')    # pelo menos 1 (validar no form)
#
# class Necessidade(models.Model):                       # RF-13, RN-02, RN-21
#     ong        ForeignKey(Ong, on_delete=CASCADE, related_name='necessidades')
#     titulo     CharField(max_length=120)
#     descricao  TextField(blank=True)
#     tipo       CharField(choices=TipoNecessidade.choices)
#     unidade    CharField(max_length=30)                # ex.: 'cestas', 'kg', 'voluntários', 'R$'
#     meta       DecimalField(max_digits=10, decimal_places=2)
#     situacao   CharField(choices=SituacaoNecessidade.choices, default=ABERTA)
#     criada_em  DateTimeField(auto_now_add=True)
#     Meta: ordering = ['-criada_em']
#     Propriedades calculadas (mesmo nome dos mocks): confirmado, percentual
#
# Os testes de tests/ estão marcados com skip: remova o skip do teste ao implementar o item.
# ---------------------------------------------------------------------------------------------
