"""Dados mock do app colheita (ADR-004). Distâncias calculadas a partir de Ceilândia.

MOCK: na camada 1, saldo e distancia_km passam a ser calculados (BL-33, BL-34, ADR-003).
"""
from datetime import date
from decimal import Decimal

from core.mocks_util import lista, obj
from ongs.mocks import LOCALIDADES, ONGS

_LOCAL = {l.nome: l for l in LOCALIDADES}

# O e-mail fica no Usuario, ligado ao PerfilPessoa por perfil.usuario (RF-27)
def _agricultor(nome_completo, telefone, email):
    return obj(nome_completo=nome_completo, telefone=telefone, usuario=obj(email=email))


_AGRICULTORES = {
    'Antônio Ribeiro': _agricultor('Antônio Ribeiro', '(61) 98123-4567', 'antonio.ribeiro@exemplo.com'),
    'Lúcia Ferreira': _agricultor('Lúcia Ferreira', '(61) 99654-2210', 'lucia.ferreira@exemplo.com'),
    'José Almeida': _agricultor('José Almeida', '(61) 98877-1122', 'jose.almeida@exemplo.com'),
    'Rosa Nunes': _agricultor('Rosa Nunes', '(61) 99210-3344', 'rosa.nunes@exemplo.com'),
    'Carlos Menezes': _agricultor('Carlos Menezes', '(61) 98400-5566', 'carlos.menezes@exemplo.com'),
}


def _oferta(pk, produto, categoria, quantidade, saldo, unidade, localidade, distancia, colher_ate, estado,
            destino, preco, transporte, agricultor, retirada, urgente=False, ong_destino=None):
    return obj(pk=pk, produto=produto, categoria=categoria, quantidade=Decimal(quantidade),
               saldo=Decimal(saldo), unidade=unidade, localidade=_LOCAL[localidade], distancia_km=distancia,
               colher_ate=colher_ate, estado=estado, destino=destino,
               preco_unitario=Decimal(preco) if preco else None, transporte=transporte,
               agricultor=_AGRICULTORES[agricultor], local_retirada=retirada, situacao='aberta',
               urgente=urgente, vencida=False, ong_destino=ong_destino)


OFERTAS = lista(
    _oferta(106, 'Couve-manteiga', 'hortalicas', 30, 30, 'un', 'Brazlândia', 21, date(2026, 10, 24), 'excedente',
            'doar', None, 'ong_busca', 'Antônio Ribeiro', 'Chácara 12, Núcleo Rural Alexandre Gusmão',
            ong_destino=ONGS[0]),
    _oferta(101, 'Alface crespa', 'hortalicas', 40, 25, 'un', 'Brazlândia', 21, date(2026, 10, 18), 'excedente',
            'doar', None, 'ong_busca', 'Antônio Ribeiro', 'Chácara 12, Núcleo Rural Alexandre Gusmão',
            urgente=True),
    _oferta(102, 'Mandioca', 'raizes_tuberculos', 200, 200, 'kg', 'Ceilândia', 0, date(2026, 10, 30), 'excedente',
            'doar', None, 'ong_busca', 'Lúcia Ferreira', 'Sítio Boa Vista, Setor de Chácaras do Sol Nascente'),
    _oferta(103, 'Abóbora cabotiá', 'hortalicas', 150, 60, 'kg', 'Gama', 26, date(2026, 10, 25), 'fora_do_padrao',
            'vender', '1.80', 'agricultor_leva', 'José Almeida', 'Núcleo Rural Ponte Alta, lote 8'),
    _oferta(104, 'Banana-prata', 'frutas', 80, 80, 'kg', 'Sobradinho', 38, date(2026, 10, 21), 'fora_do_padrao',
            'doar', None, 'agricultor_leva', 'Rosa Nunes', 'Chácara Recanto, DF-150 km 4'),
    _oferta(105, 'Tomate', 'hortalicas', 120, '85.5', 'kg', 'Planaltina', 52, date(2026, 10, 22), 'fora_do_padrao',
            'vender', '2.50', 'agricultor_leva', 'Carlos Menezes', 'Núcleo Rural Taquara, chácara 31'),
)

# Reservas da Cozinha Solidária Sol Nascente (Tela 11)
RESERVAS_DA_ONG = lista(
    obj(pk=1, oferta=OFERTAS[1], quantidade=Decimal(15), situacao='ativa', quantidade_recebida=None,
        recebida_em=None, criada_em=date(2026, 10, 15)),
    obj(pk=2, oferta=OFERTAS[2], quantidade=Decimal(50), situacao='recebida', quantidade_recebida=Decimal(48),
        recebida_em=date(2026, 10, 10), criada_em=date(2026, 10, 8)),
)

# Ofertas do agricultor Antônio Ribeiro (Tela 13)
OFERTAS_DO_AGRICULTOR = lista(OFERTAS[1], OFERTAS[0])
