"""CNPJs fictícios para a carga de demonstração (RN-24, E-11).

Só gera números com os dígitos verificadores certos. A validação do CNPJ no cadastro da ONG
é do BL-29 (RF-10).
"""

_PESOS_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_PESOS_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


def _digito(numeros, pesos):
    resto = sum(int(n) * p for n, p in zip(numeros, pesos)) % 11
    return '0' if resto < 2 else str(11 - resto)


def digitos_verificadores(doze_digitos):
    """Os dois últimos dígitos de um CNPJ, calculados a partir dos 12 primeiros."""
    primeiro = _digito(doze_digitos, _PESOS_1)
    return primeiro + _digito(doze_digitos + primeiro, _PESOS_2)


def gerar_cnpj(numero):
    """CNPJ fictício, só com dígitos, a partir de um número de 1 a 9.999.999.

    Números diferentes geram CNPJs diferentes (RN-24): a raiz é 4 seguido do número com 7 dígitos,
    e a filial é sempre 0001.
    """
    if not 1 <= numero <= 9_999_999:
        raise ValueError('O número precisa estar entre 1 e 9.999.999.')
    doze = f'4{numero:07d}0001'
    return doze + digitos_verificadores(doze)
