"""Dados mock do painel de impacto (ADR-004). MOCK: trocar pelos cálculos de painel.services (BL-37)."""
from decimal import Decimal

from core.mocks_util import obj
from ongs.mocks import ODS

_ODS = {o.numero: o for o in ODS}

INDICADORES = obj(kg_salvos=Decimal(4380), familias_atendidas=760, renda_gerada=Decimal('3912.50'), ongs_ativas=6)

# (mês, kg recebidos) pela data do recebimento (RN-23)
KG_POR_MES = [('mai', 320), ('jun', 540), ('jul', 610), ('ago', 880), ('set', 1130), ('out', 900)]

# (ODS, percentual das ações confirmadas) (RN-07)
FATIA_POR_ODS = [(_ODS[2], 34), (_ODS[1], 22), (_ODS[10], 18), (_ODS[4], 12), (_ODS[8], 9), (_ODS[5], 5)]
