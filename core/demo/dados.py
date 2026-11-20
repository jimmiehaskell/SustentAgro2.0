"""Dados fictícios da carga de demonstração (BL-27, Pedro). RF-32, RN-24, P-06, E-10.

Só dados: quem grava no banco é o comando carregar_demo (parte 3, depois do BL-24 ao BL-26).
Os nomes das chaves são os nomes de campo do modelo de dados (comentários dos models.py), e os textos
são os mesmos das telas mock, para as telas continuarem iguais depois da troca para o banco.

Datas relativas, para a demonstração nunca ficar com tudo vencido:
- colher_em_dias: quantos dias depois de hoje vence a oferta aberta;
- meses_atras e dia: mês e dia do recebimento no histórico (0 = mês atual; no mês atual,
  a carga usa no máximo o dia de hoje).
"""
from decimal import Decimal as D

from core.demo.cnpj import gerar_cnpj

# P-06: regiões administrativas do DF e municípios do Entorno. Coordenadas aproximadas do centro
# de cada uma, suficientes para a distância em linha reta (RN-15).
LOCALIDADES = [
    # (nome, uf, latitude, longitude)
    ('Águas Claras', 'DF', D('-15.839000'), D('-48.027000')),
    ('Brazlândia', 'DF', D('-15.675800'), D('-48.200300')),
    ('Ceilândia', 'DF', D('-15.819700'), D('-48.108300')),
    ('Gama', 'DF', D('-16.018100'), D('-48.061400')),
    ('Guará', 'DF', D('-15.825600'), D('-47.980600')),
    ('Itapoã', 'DF', D('-15.748000'), D('-47.768000')),
    ('Núcleo Bandeirante', 'DF', D('-15.870500'), D('-47.968600')),
    ('Paranoá', 'DF', D('-15.774400'), D('-47.779700')),
    ('Planaltina', 'DF', D('-15.621400'), D('-47.649200')),
    ('Plano Piloto', 'DF', D('-15.793900'), D('-47.882800')),
    ('Recanto das Emas', 'DF', D('-15.905000'), D('-48.064000')),
    ('Riacho Fundo', 'DF', D('-15.883300'), D('-48.016700')),
    ('Samambaia', 'DF', D('-15.878900'), D('-48.087000')),
    ('Santa Maria', 'DF', D('-16.019400'), D('-48.012800')),
    ('São Sebastião', 'DF', D('-15.902800'), D('-47.778400')),
    ('Sobradinho', 'DF', D('-15.653300'), D('-47.789400')),
    ('Sol Nascente/Pôr do Sol', 'DF', D('-15.800000'), D('-48.133000')),
    ('Taguatinga', 'DF', D('-15.833500'), D('-48.056400')),
    ('Vicente Pires', 'DF', D('-15.803000'), D('-48.028000')),
    ('Águas Lindas de Goiás', 'GO', D('-15.761700'), D('-48.281600')),
    ('Cidade Ocidental', 'GO', D('-16.076000'), D('-47.925000')),
    ('Formosa', 'GO', D('-15.537200'), D('-47.334000')),
    ('Luziânia', 'GO', D('-16.252500'), D('-47.950300')),
    ('Novo Gama', 'GO', D('-16.059000'), D('-48.042000')),
    ('Planaltina de Goiás', 'GO', D('-15.452800'), D('-47.613600')),
    ('Santo Antônio do Descoberto', 'GO', D('-15.941100'), D('-48.257800')),
    ('Valparaíso de Goiás', 'GO', D('-16.065100'), D('-47.975700')),
]

# Catálogo fixo de ODS (D-14)
ODS = [
    # (numero, nome, cor)
    (1, 'Erradicação da pobreza', '#E5243B'),
    (2, 'Fome zero e agricultura sustentável', '#DDA63A'),
    (4, 'Educação de qualidade', '#C5192D'),
    (5, 'Igualdade de gênero', '#FF3A21'),
    (8, 'Trabalho decente e crescimento econômico', '#A21942'),
    (10, 'Redução das desigualdades', '#DD1367'),
]

# PerfilPessoa com eh_agricultor = True (localidade obrigatória para agricultor)
AGRICULTORES = [
    {'username': 'antonio.ribeiro', 'nome_completo': 'Antônio Ribeiro', 'telefone': '(61) 98123-4567',
     'email': 'antonio.ribeiro@exemplo.com', 'localidade': 'Brazlândia'},
    {'username': 'lucia.ferreira', 'nome_completo': 'Lúcia Ferreira', 'telefone': '(61) 99654-2210',
     'email': 'lucia.ferreira@exemplo.com', 'localidade': 'Ceilândia'},
    {'username': 'jose.almeida', 'nome_completo': 'José Almeida', 'telefone': '(61) 98877-1122',
     'email': 'jose.almeida@exemplo.com', 'localidade': 'Gama'},
    {'username': 'rosa.nunes', 'nome_completo': 'Rosa Nunes', 'telefone': '(61) 99210-3344',
     'email': 'rosa.nunes@exemplo.com', 'localidade': 'Sobradinho'},
    {'username': 'carlos.menezes', 'nome_completo': 'Carlos Menezes', 'telefone': '(61) 98400-5566',
     'email': 'carlos.menezes@exemplo.com', 'localidade': 'Planaltina'},
]

# PerfilPessoa com eh_doador = True (localidade opcional)
DOADORES = [
    {'username': 'mariana.costa', 'nome_completo': 'Mariana Costa', 'telefone': '(61) 99812-4433',
     'email': 'mariana.costa@exemplo.com', 'localidade': None},
    {'username': 'joao.lima', 'nome_completo': 'João Pedro Lima', 'telefone': '(61) 98444-1290',
     'email': 'joao.lima@exemplo.com', 'localidade': 'Taguatinga'},
    {'username': 'carlos.souza', 'nome_completo': 'Carlos Souza', 'telefone': '(61) 99100-2030',
     'email': 'carlos.souza@exemplo.com', 'localidade': 'Guará'},
]


def _necessidade(titulo, tipo, unidade, meta, situacao='aberta'):
    return {'titulo': titulo, 'tipo': tipo, 'unidade': unidade, 'meta': D(meta), 'situacao': situacao}


# 'chave' só serve para as ofertas e reservas abaixo apontarem para a ONG; não é campo do model.
# O CNPJ é gerado com dígitos verificadores válidos e sem repetir (RN-24, E-11).
ONGS = [
    {'chave': 'sol', 'username': 'solnascente', 'nome': 'Cozinha Solidária Sol Nascente',
     'nome_curto': 'Sol Nascente', 'cnpj': gerar_cnpj(1), 'localidade': 'Ceilândia',
     'slogan': 'Comida de verdade no prato de quem mais precisa.',
     'descricao': 'Servimos almoço de segunda a sábado para famílias do Sol Nascente. Usamos hortaliças doadas por '
                  'agricultores da região e mantemos uma horta escola com as mães atendidas.',
     'telefone': '(61) 3371-0045', 'email_contato': 'contato@solnascente.org.br',
     'chave_pix': 'pix@solnascente.org.br', 'familias_por_mes': 180,
     'aceita_itens': True, 'aceita_dinheiro': True, 'aceita_voluntariado': True,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [1, 2],
     'necessidades': [
         _necessidade('Cestas básicas', 'itens', 'cestas', '60'),
         _necessidade('Voluntários para a cozinha aos sábados', 'voluntariado', 'voluntários', '8'),
         _necessidade('Gás de cozinha para o trimestre', 'dinheiro', 'R$', '1200'),
         _necessidade('Arroz (pacotes de 5 kg)', 'itens', 'pacotes', '30', 'atendida'),
     ]},
    {'chave': 'semear', 'username': 'semearsaberes', 'nome': 'Instituto Semear Saberes',
     'nome_curto': 'Semear Saberes', 'cnpj': gerar_cnpj(2), 'localidade': 'Planaltina',
     'slogan': 'Reforço escolar e leitura para crianças da zona rural.',
     'descricao': 'Atendemos crianças de 6 a 14 anos dos núcleos rurais de Planaltina no contraturno escolar.',
     'telefone': '(61) 3388-2210', 'email_contato': 'ola@semearsaberes.org',
     'chave_pix': '', 'familias_por_mes': 95,
     'aceita_itens': True, 'aceita_dinheiro': False, 'aceita_voluntariado': True,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [4, 10],
     'necessidades': [
         _necessidade('Kits de material escolar', 'itens', 'kits', '150'),
         _necessidade('Professores voluntários de reforço', 'voluntariado', 'voluntários', '6'),
     ]},
    {'chave': 'mulheres', 'username': 'mulheresdocerrado', 'nome': 'Rede Mulheres do Cerrado',
     'nome_curto': 'Mulheres do Cerrado', 'cnpj': gerar_cnpj(3), 'localidade': 'Brazlândia',
     'slogan': 'Renda e autonomia para agricultoras e costureiras.',
     'descricao': 'Grupo de produção de mulheres agricultoras que transforma excedente em conservas.',
     'telefone': '(61) 3391-7788', 'email_contato': 'rede@mulheresdocerrado.org',
     'chave_pix': 'pix@mulheresdocerrado.org', 'familias_por_mes': 60,
     'aceita_itens': False, 'aceita_dinheiro': True, 'aceita_voluntariado': True,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [5, 8],
     'necessidades': [
         _necessidade('Máquinas de costura para a oficina', 'dinheiro', 'R$', '4000'),
     ]},
    {'chave': 'prato', 'username': 'pratocheio', 'nome': 'Associação Prato Cheio Gama',
     'nome_curto': 'Prato Cheio', 'cnpj': gerar_cnpj(4), 'localidade': 'Gama',
     'slogan': 'Sopa comunitária três vezes por semana.',
     'descricao': 'Preparamos sopa com hortaliças da Colheita Solidária para famílias do Gama e de Santa Maria.',
     'telefone': '(61) 3556-1020', 'email_contato': 'pratocheio@email.org',
     'chave_pix': '', 'familias_por_mes': 210,
     'aceita_itens': True, 'aceita_dinheiro': False, 'aceita_voluntariado': False,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [2, 10],
     'necessidades': [
         _necessidade('Hortaliças para a sopa comunitária', 'itens', 'kg', '300'),
     ]},
    {'chave': 'casa', 'username': 'casaesperanca', 'nome': 'Casa Esperança Águas Lindas',
     'nome_curto': 'Casa Esperança', 'cnpj': gerar_cnpj(5), 'localidade': 'Águas Lindas de Goiás',
     'slogan': 'Acolhimento para mães e bebês do Entorno.',
     'descricao': 'Apoio a gestantes e mães com bebês de até 2 anos em Águas Lindas de Goiás.',
     'telefone': '(61) 3613-4400', 'email_contato': 'casaesperanca@email.org',
     'chave_pix': 'casaesperanca@email.org', 'familias_por_mes': 140,
     'aceita_itens': True, 'aceita_dinheiro': True, 'aceita_voluntariado': False,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [1, 4],
     'necessidades': [
         _necessidade('Fraldas infantis', 'itens', 'pacotes', '400'),
     ]},
    {'chave': 'jqt', 'username': 'juventudequetrabalha', 'nome': 'Projeto Juventude que Trabalha',
     'nome_curto': 'Juventude que Trabalha', 'cnpj': gerar_cnpj(6), 'localidade': 'Samambaia',
     'slogan': 'Primeiro emprego com mentoria de quem já chegou lá.',
     'descricao': 'Oficinas de currículo, entrevistas simuladas e mentoria para jovens de 16 a 24 anos.',
     'telefone': '(61) 3359-0900', 'email_contato': 'jqt@email.org',
     'chave_pix': '', 'familias_por_mes': 75,
     'aceita_itens': False, 'aceita_dinheiro': False, 'aceita_voluntariado': True,
     'situacao': 'ativa', 'motivo_reprovacao': '', 'ods': [8, 10],
     'necessidades': [
         _necessidade('Mentores de primeiro emprego', 'voluntariado', 'voluntários', '10'),
     ]},
    # Para as telas de situação da ONG (perfis ong-pendente e ong-reprovada); não aparecem no site (RN-01)
    {'chave': 'horta', 'username': 'hortavilaplanalto', 'nome': 'Horta Comunitária Vila Planalto',
     'nome_curto': 'Horta Vila Planalto', 'cnpj': gerar_cnpj(7), 'localidade': 'Plano Piloto',
     'slogan': '', 'descricao': '', 'telefone': '(61) 3301-2200', 'email_contato': 'contato@hortavilaplanalto.org',
     'chave_pix': '', 'familias_por_mes': 40,
     'aceita_itens': True, 'aceita_dinheiro': False, 'aceita_voluntariado': True,
     'situacao': 'pendente', 'motivo_reprovacao': '', 'ods': [2], 'necessidades': []},
    {'chave': 'raizes', 'username': 'raizesdoplanalto', 'nome': 'Instituto Raízes do Planalto',
     'nome_curto': 'Raízes do Planalto', 'cnpj': gerar_cnpj(8), 'localidade': 'Planaltina',
     'slogan': '', 'descricao': '', 'telefone': '(61) 3302-4400', 'email_contato': 'contato@raizesdoplanalto.org',
     'chave_pix': '', 'familias_por_mes': 40,
     'aceita_itens': True, 'aceita_dinheiro': False, 'aceita_voluntariado': True,
     'situacao': 'reprovada', 'ods': [2],
     'motivo_reprovacao': 'O CNPJ informado pertence a uma empresa com fins lucrativos, não a uma organização '
                          'da sociedade civil.',
     'necessidades': []},
]

_RETIRADA = {
    'antonio.ribeiro': 'Chácara 12, Núcleo Rural Alexandre Gusmão',
    'lucia.ferreira': 'Sítio Boa Vista, Setor de Chácaras do Sol Nascente',
    'jose.almeida': 'Núcleo Rural Ponte Alta, lote 8',
    'rosa.nunes': 'Chácara Recanto, DF-150 km 4',
    'carlos.menezes': 'Núcleo Rural Taquara, chácara 31',
}
_LOCAL_DO_AGRICULTOR = {a['username']: a['localidade'] for a in AGRICULTORES}


def _oferta(agricultor, produto, categoria, quantidade, unidade, estado, destino, transporte,
            preco=None, reservas=(), **extra):
    return {'agricultor': agricultor, 'produto': produto, 'categoria': categoria, 'quantidade': D(quantidade),
            'unidade': unidade, 'localidade': _LOCAL_DO_AGRICULTOR[agricultor], 'estado': estado,
            'destino': destino, 'preco_unitario': D(preco) if preco else None,
            'local_retirada': _RETIRADA[agricultor], 'transporte': transporte, 'reservas': list(reservas), **extra}


def _ativa(ong, quantidade):
    return {'ong': ong, 'quantidade': D(quantidade), 'situacao': 'ativa'}


def _recebida(ong, quantidade_recebida):
    return {'ong': ong, 'quantidade': D(quantidade_recebida), 'situacao': 'recebida',
            'quantidade_recebida': D(quantidade_recebida)}


# Ofertas abertas: as mesmas das telas mock (Ofertas, Minhas ofertas, Minhas reservas)
OFERTAS_ABERTAS = [
    _oferta('antonio.ribeiro', 'Alface crespa', 'hortalicas', '40', 'un', 'excedente', 'doar', 'ong_busca',
            reservas=[_ativa('sol', '15')], colher_em_dias=2, ong_destino=None),
    _oferta('lucia.ferreira', 'Mandioca', 'raizes_tuberculos', '200', 'kg', 'excedente', 'doar', 'ong_busca',
            colher_em_dias=14, ong_destino=None),
    _oferta('jose.almeida', 'Abóbora cabotiá', 'hortalicas', '150', 'kg', 'fora_do_padrao', 'vender',
            'agricultor_leva', preco='1.80', reservas=[_ativa('prato', '90')], colher_em_dias=9, ong_destino=None),
    _oferta('rosa.nunes', 'Banana-prata', 'frutas', '80', 'kg', 'fora_do_padrao', 'doar', 'agricultor_leva',
            colher_em_dias=5, ong_destino=None),
    _oferta('carlos.menezes', 'Tomate', 'hortalicas', '120', 'kg', 'fora_do_padrao', 'vender', 'agricultor_leva',
            preco='2.50', reservas=[_ativa('casa', '34.5')], colher_em_dias=6, ong_destino=None),
    # RN-04: direcionada à Sol Nascente nas primeiras 48 h
    _oferta('antonio.ribeiro', 'Couve-manteiga', 'hortalicas', '30', 'un', 'excedente', 'doar', 'ong_busca',
            colher_em_dias=8, ong_destino='sol'),
]

# Histórico de colheitas já recebidas, para o painel (RF-29 a RF-31). Os kg recebidos por mês são os do
# gráfico mock: 320, 540, 610, 880, 1.130 e 900 (de 5 meses atrás até o mês atual). As ONGs que recebem
# cobrem os 6 ODS, para a fatia por ODS ter números variados (E-10).
HISTORICO = [
    _oferta('lucia.ferreira', 'Mandioca', 'raizes_tuberculos', '200', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('sol', '180')], meses_atras=5, dia=8),
    _oferta('rosa.nunes', 'Banana-prata', 'frutas', '150', 'kg', 'fora_do_padrao', 'doar', 'agricultor_leva',
            reservas=[_recebida('prato', '140')], meses_atras=5, dia=21),
    _oferta('jose.almeida', 'Abóbora cabotiá', 'hortalicas', '360', 'kg', 'fora_do_padrao', 'vender',
            'agricultor_leva', preco='1.50', reservas=[_recebida('prato', '200'), _recebida('casa', '140')],
            meses_atras=4, dia=6),
    _oferta('antonio.ribeiro', 'Repolho', 'hortalicas', '220', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('sol', '200')], meses_atras=4, dia=18),
    _oferta('carlos.menezes', 'Tomate', 'hortalicas', '260', 'kg', 'fora_do_padrao', 'vender', 'agricultor_leva',
            preco='2.50', reservas=[_recebida('semear', '120'), _recebida('sol', '130')], meses_atras=3, dia=10),
    _oferta('jose.almeida', 'Chuchu', 'hortalicas', '380', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('prato', '360')], meses_atras=3, dia=24),
    _oferta('lucia.ferreira', 'Mandioca', 'raizes_tuberculos', '400', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('sol', '300'), _recebida('jqt', '100')], meses_atras=2, dia=5),
    _oferta('rosa.nunes', 'Laranja-pera', 'frutas', '500', 'kg', 'fora_do_padrao', 'vender', 'agricultor_leva',
            preco='1.20', reservas=[_recebida('casa', '280'), _recebida('mulheres', '200')], meses_atras=2, dia=19),
    _oferta('jose.almeida', 'Abóbora cabotiá', 'hortalicas', '650', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('prato', '450'), _recebida('casa', '180')], meses_atras=1, dia=7),
    _oferta('carlos.menezes', 'Batata-doce', 'raizes_tuberculos', '520', 'kg', 'excedente', 'doar', 'ong_busca',
            reservas=[_recebida('semear', '250'), _recebida('mulheres', '250')], meses_atras=1, dia=22),
    _oferta('rosa.nunes', 'Banana-prata', 'frutas', '500', 'kg', 'fora_do_padrao', 'doar', 'agricultor_leva',
            reservas=[_recebida('sol', '300'), _recebida('jqt', '150')], meses_atras=0, dia=3),
    _oferta('carlos.menezes', 'Tomate', 'hortalicas', '450', 'kg', 'fora_do_padrao', 'vender', 'agricultor_leva',
            preco='2.80', reservas=[_recebida('prato', '450')], meses_atras=0, dia=12),
    # Em unidades: entra na renda (RN-09), mas não nos kg salvos (RN-08, P-01). É a vencida da Minhas ofertas.
    _oferta('antonio.ribeiro', 'Milho verde', 'graos', '300', 'un', 'excedente', 'vender', 'ong_busca',
            preco='0.80', reservas=[_recebida('sol', '150'), _recebida('semear', '110')], meses_atras=0, dia=1),
]
