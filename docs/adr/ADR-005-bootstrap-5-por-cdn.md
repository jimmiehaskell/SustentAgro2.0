# ADR-005 — Bootstrap 5 por CDN como único framework de CSS

## Status
Aceito (15/10/2026)

## Contexto
O código atual mistura Bootstrap 4 e Tailwind v3 (`base.html`) com Tailwind v4 (`login.html`), todos por CDN. Todas as telas precisam funcionar no celular (RNF-01, D-23). Quatro pessoas vão montar telas em paralelo, e o visual precisa ficar consistente (R-04). O painel precisa de um gráfico de barras (RF-30).

## Decisão
Bootstrap 5 por CDN, com versão fixa, mais um único arquivo de estilos do projeto (`core/static/css/sustentagro.css`) para cores e ajustes. Os componentes repetidos (cartão de ONG, selo de ODS, barra de progresso, cartão de oferta) viram templates parciais usados com `{% include %}`, feitos no M1. O gráfico usa Chart.js por CDN. Saem o Tailwind, o Bootstrap 4, o `package.json` e o `package-lock.json`.

## Paleta e tipografia (D-32, 16/10/2026)
As variáveis do Bootstrap são sobrescritas no `sustentagro.css` com a paleta "Campo suave": `--bs-primary` `#3D7A16`, limão suave `#A6E36B` só em detalhes, verde claro de apoio `#EAF7DC`, carvão `#1D1F1C`. O tema escuro usa o modo de cor do Bootstrap 5.3 (`data-bs-theme="dark"`), definido pelo tema do sistema e alternável por um botão. Títulos em Montserrat (D-33; antes, Bricolage Grotesque) e texto em Figtree, pelo Google Fonts. Os valores exatos dos dois temas estão no `:root` do `prototipo.html`.

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| Tailwind com build (npm) | Exige Node e uma etapa de build no projeto e na imagem Docker; classes utilitárias são mais difíceis de manter consistentes por iniciantes |
| CSS próprio, sem framework | Responsividade e componentes ficariam todos por conta da equipe, com 4 semanas de prazo |
| Manter o Bootstrap 4 | Versão sem suporte; o 5 dispensa o jQuery |

Escolha do usuário em 15/10/2026.

## Consequências
- Sem etapa de build: o grupo edita HTML e CSS e vê o resultado na hora.
- O CDN depende de internet. Se a apresentação usar o plano B local (R-09), o notebook precisa de internet, ou os arquivos do Bootstrap e do Chart.js devem ser copiados para `static/`.
- O carrossel atual precisa de um ajuste pequeno (atributos `data-bs-*`).

## Requisitos relacionados
RNF-01, RF-30, R-04, D-23
