# ADR-003 — PostgreSQL na VPS, SQLite local e reserva protegida por transação

## Status
Aceito (15/10/2026)

## Contexto
A VPS exige o banco em container próprio, numa rede interna (RNF-02), e já usa PostgreSQL 18 no outro projeto do servidor. Os devs usam Windows, e não se presume que saibam Docker. Duas ONGs podem reservar a mesma oferta ao mesmo tempo, e a soma das reservas nunca pode passar da quantidade publicada (UC-09, RN-03). A distância é calculada entre localidades com latitude e longitude (RN-15).

## Decisão
- **Produção:** PostgreSQL 18 em container. **Local:** SQLite. O `settings.py` escolhe o banco pelas variáveis do `.env`: sem `DB_NAME`, usa SQLite.
- **Reserva:** a função `reservar_oferta` roda dentro de `transaction.atomic()` e trava a linha da oferta com `select_for_update()` antes de recalcular o saldo.
- **Saldo:** não fica guardado em coluna. É calculado como quantidade publicada menos a soma das reservas ativas e recebidas, o que torna RN-03 verificável num só lugar.
- **Distância:** fórmula de haversine em Python sobre as coordenadas das localidades. A lista de ofertas é pequena (dados de demonstração), então o cálculo é feito na própria consulta da lista.
- **Quantidades:** `DecimalField` com uma casa decimal; para unidades, a validação exige número inteiro (RN-16).

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| PostgreSQL também local, via Docker | Exigiria Docker Desktop e noções de Compose de cada dev, sem ganho para um projeto deste tamanho (decisão do usuário, 15/10/2026) |
| Saldo guardado numa coluna e atualizado a cada reserva | Duplica informação; um erro numa das operações deixa saldo e reservas inconsistentes |
| PostGIS ou geocodificação para a distância | Fora do escopo (D-27); haversine entre localidades basta |

## Consequências
- Diferenças entre SQLite e PostgreSQL só aparecem no CI (ADR-006) e na VPS. Por isso o CI roda contra PostgreSQL.
- No SQLite, `select_for_update()` é ignorado, mas o próprio SQLite serializa as escritas. A proteção contra reservas simultâneas só é exercitada de verdade no PostgreSQL.
- Filtrar ofertas "até 30 km" exige calcular a distância de todas as ofertas visíveis. Isso é aceitável com dezenas de ofertas, não com milhares.

## Requisitos relacionados
RNF-02, RN-03, RN-15, RN-16, RF-19, RF-20, UC-09
