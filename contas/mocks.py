"""Dados demonstrativos do perfil de pessoa (BL-13, ADR-004)."""

from core.mocks_util import obj


# MOCK: trocar na camada 3 (BL-48) pelo PerfilPessoa da conta autenticada.
PERFIL_PESSOA = obj(nome_completo='Mariana Costa', eh_doador=True, eh_agricultor=False)
