"""Dados mock do app ongs (ADR-004): mesmos nomes de campo do modelo de dados.

MOCK: na camada 1, as views trocam estas listas por consultas ao banco (BL-30).
Campos calculados (confirmado, percentual) aparecem prontos aqui; no banco, viram
propriedades ou anotações com o mesmo nome.
"""
from decimal import Decimal

from core.mocks_util import lista, obj

ODS = lista(
    obj(numero=1, nome='Erradicação da pobreza', cor='#E5243B'),
    obj(numero=2, nome='Fome zero e agricultura sustentável', cor='#DDA63A'),
    obj(numero=4, nome='Educação de qualidade', cor='#C5192D'),
    obj(numero=5, nome='Igualdade de gênero', cor='#FF3A21'),
    obj(numero=8, nome='Trabalho decente e crescimento econômico', cor='#A21942'),
    obj(numero=10, nome='Redução das desigualdades', cor='#DD1367'),
)
_ODS = {o.numero: o for o in ODS}

LOCALIDADES = lista(*[obj(nome=n, uf=uf) for n, uf in [
    ('Brazlândia', 'DF'), ('Ceilândia', 'DF'), ('Gama', 'DF'), ('Planaltina', 'DF'), ('Samambaia', 'DF'),
    ('Sobradinho', 'DF'), ('Taguatinga', 'DF'), ('Águas Lindas de Goiás', 'GO'), ('Valparaíso de Goiás', 'GO'),
]])
_LOCAL = {l.nome: l for l in LOCALIDADES}


def _necessidade(pk, titulo, tipo, unidade, meta, confirmado, situacao='aberta'):
    meta, confirmado = Decimal(meta), Decimal(confirmado)
    return obj(pk=pk, titulo=titulo, descricao='', tipo=tipo, unidade=unidade, meta=meta,
               confirmado=confirmado, situacao=situacao,
               percentual=min(100, int(confirmado / meta * 100)))


def _ong(pk, nome, nome_curto, localidade, slogan, ods, aceita, familias, telefone, email, pix, descricao,
         necessidades, motivo_reprovacao=''):
    return obj(pk=pk, nome=nome, nome_curto=nome_curto, localidade=_LOCAL[localidade], slogan=slogan,
               descricao=descricao, logo=None, capa=None, telefone=telefone, email_contato=email, site='',
               chave_pix=pix, familias_por_mes=familias, aceita_itens='itens' in aceita,
               aceita_dinheiro='dinheiro' in aceita, aceita_voluntariado='voluntariado' in aceita,
               situacao='ativa', motivo_reprovacao=motivo_reprovacao,
               ods=lista(*[_ODS[n] for n in ods]), necessidades=lista(*necessidades))


ONGS = lista(
    _ong(1, 'Cozinha Solidária Sol Nascente', 'Sol Nascente', 'Ceilândia',
         'Comida de verdade no prato de quem mais precisa.', [1, 2], 'itens dinheiro voluntariado', 180,
         '(61) 3371-0045', 'contato@solnascente.org.br', 'pix@solnascente.org.br',
         'Servimos almoço de segunda a sábado para famílias do Sol Nascente. Usamos hortaliças doadas por '
         'agricultores da região e mantemos uma horta escola com as mães atendidas.',
         [_necessidade(11, 'Cestas básicas', 'itens', 'cestas', 60, 42),
          _necessidade(12, 'Voluntários para a cozinha aos sábados', 'voluntariado', 'voluntários', 8, 5),
          _necessidade(13, 'Gás de cozinha para o trimestre', 'dinheiro', 'R$', 1200, 380),
          _necessidade(14, 'Arroz (pacotes de 5 kg)', 'itens', 'pacotes', 30, 30, 'atendida')]),
    _ong(2, 'Instituto Semear Saberes', 'Semear Saberes', 'Planaltina',
         'Reforço escolar e leitura para crianças da zona rural.', [4, 10], 'itens voluntariado', 95,
         '(61) 3388-2210', 'ola@semearsaberes.org', '',
         'Atendemos crianças de 6 a 14 anos dos núcleos rurais de Planaltina no contraturno escolar.',
         [_necessidade(21, 'Kits de material escolar', 'itens', 'kits', 150, 70),
          _necessidade(22, 'Professores voluntários de reforço', 'voluntariado', 'voluntários', 6, 3)]),
    _ong(3, 'Rede Mulheres do Cerrado', 'Mulheres do Cerrado', 'Brazlândia',
         'Renda e autonomia para agricultoras e costureiras.', [5, 8], 'dinheiro voluntariado', 60,
         '(61) 3391-7788', 'rede@mulheresdocerrado.org', '12.345.678/0001-95',
         'Grupo de produção de mulheres agricultoras que transforma excedente em conservas.',
         [_necessidade(31, 'Máquinas de costura para a oficina', 'dinheiro', 'R$', 4000, 2150)]),
    _ong(4, 'Associação Prato Cheio Gama', 'Prato Cheio', 'Gama',
         'Sopa comunitária três vezes por semana.', [2, 10], 'itens', 210,
         '(61) 3556-1020', 'pratocheio@email.org', '',
         'Preparamos sopa com hortaliças da Colheita Solidária para famílias do Gama e de Santa Maria.',
         [_necessidade(41, 'Hortaliças para a sopa comunitária', 'itens', 'kg', 300, 120)]),
    _ong(5, 'Casa Esperança Águas Lindas', 'Casa Esperança', 'Águas Lindas de Goiás',
         'Acolhimento para mães e bebês do Entorno.', [1, 4], 'itens dinheiro', 140,
         '(61) 3613-4400', 'casaesperanca@email.org', 'casaesperanca@email.org',
         'Apoio a gestantes e mães com bebês de até 2 anos em Águas Lindas de Goiás.',
         [_necessidade(51, 'Fraldas infantis', 'itens', 'pacotes', 400, 210)]),
    _ong(6, 'Projeto Juventude que Trabalha', 'Juventude que Trabalha', 'Samambaia',
         'Primeiro emprego com mentoria de quem já chegou lá.', [8, 10], 'voluntariado', 75,
         '(61) 3359-0900', 'jqt@email.org', '',
         'Oficinas de currículo, entrevistas simuladas e mentoria para jovens de 16 a 24 anos.',
         [_necessidade(61, 'Mentores de primeiro emprego', 'voluntariado', 'voluntários', 10, 4)]),
)


def ong_por_pk(pk):
    return next((o for o in ONGS if o.pk == pk), None)


def precisa_agora(ong):
    """Necessidade aberta mais recente, usada no cartão da lista (RF-05)."""
    return next((n for n in ong.necessidades if n.situacao == 'aberta'), None)
