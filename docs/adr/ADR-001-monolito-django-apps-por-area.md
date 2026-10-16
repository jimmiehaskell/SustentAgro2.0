# ADR-001 — Monólito Django com templates no servidor, dividido em apps por área

## Status
Aceito (15/10/2026)

## Contexto
O sistema já é um app Django 5.2 (requirements.md §0), e a equipe tem 4 devs que sabem Python e HTML/CSS, mas não Django (D-29). As telas precisam funcionar primeiro em mock e depois com banco, sem mudar de aparência (D-28). Com 4 pessoas editando ao mesmo tempo, arquivos compartilhados geram conflitos nos pull requests (R-02, R-04).

## Decisão
Uma única aplicação Django que gera o HTML no servidor (templates do Django), dividida nos apps `core`, `contas`, `ongs`, `colheita`, `doacoes` e `painel`. As regras de negócio ficam em funções de `services.py` dentro de cada app, e as views só chamam essas funções.

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| Um app só (o `ongs` atual) | Os 4 devs editariam os mesmos `models.py`, `views.py` e pasta de templates o tempo todo, com mais conflitos e revisões mais lentas (decisão do usuário, 15/10/2026) |
| API (Django REST) + frontend separado (React, Angular) | Duas tecnologias novas para quem ainda não conhece Django; dobra o trabalho com 4 pessoas e 4 semanas |
| Regras de negócio dentro das views | Regras como saldo e reserva ficariam espalhadas e difíceis de testar; `services.py` concentra o que os testes precisam cobrir (RNF-09) |

## Consequências
- Cada dev tende a trabalhar num app, o que reduz conflitos e deixa clara a responsabilidade de cada um.
- Há dependências entre apps: `colheita` usa a ONG de `ongs` e a localidade de `contas`. Por isso, os models de `contas` e `ongs` precisam existir antes dos de `colheita`, `doacoes` e `painel`.
- `services.py` é uma convenção, não algo que o Django impõe. A revisão de PR precisa cobrar que as regras não fiquem na view.

## Requisitos relacionados
OBJ-03, D-28, D-29, RNF-09, R-02, R-04
