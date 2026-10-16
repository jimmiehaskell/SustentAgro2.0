# ADR-004 — Telas mock com os mesmos nomes de campo dos models

## Status
Aceito (15/10/2026)

## Contexto
Todas as telas precisam ficar navegáveis antes do banco (D-28), e a troca de mock para dados reais não pode exigir refazer o template (R-05). Os devs começam pelo que já sabem, HTML/CSS (D-29).

## Decisão
No M1, Jimmie cria todas as rotas definitivas e as views de cada app, devolvendo dados de um arquivo `mocks.py` do próprio app. Os mocks são dicionários e listas com **exatamente os nomes de campo do modelo de dados da Fase 4a** (por exemplo, `oferta.produto`, `oferta.saldo`, `ong.localidade.nome`). Na troca, a view passa a buscar no banco e o template não muda. Cada view mock leva o comentário `# MOCK: trocar na camada N`.

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| HTML estático solto, sem Django, na fase mock | Exigiria reescrever cada tela como template depois; as URLs não seriam as definitivas |
| Popular o banco desde o começo, sem mock | Trava o frontend esperando models e regras, justamente o gargalo do plano |

## Consequências
- O modelo de dados (Fase 4a) precisa estar aprovado antes do M1, porque os mocks dependem dele.
- Campos calculados (saldo, distância, porcentagem da barra) aparecem nos mocks como valores prontos. Na troca, a view ou o model passa a calculá-los com o mesmo nome.
- Ao fim do projeto, uma busca por `MOCK` mostra o que ficou em mock.

## Requisitos relacionados
D-28, OBJ-03, R-05, todas as telas (camada 0)
