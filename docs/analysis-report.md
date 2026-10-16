# Relatório de Análise — SustentAgro 2.0

> Documento da Fase 3 (Análise). Auditoria de `requirements.md` (aprovado em 13/10/2026, revisado em 14/10/2026) e `project-plan.md` (aprovado em 14/10/2026), lidos juntos e por inteiro em 14/10/2026.

## 1. Conflitos encontrados

| ID | Onde (documento/seção) | Conflito identificado | Resolução acordada |
|---|---|---|---|
| A-01 | `project-plan.md` §1 × `requirements.md` RF-05, RF-06, RF-13 | O plano põe a lista de ONGs (RF-05, "Precisa agora") e a página da ONG (RF-06, necessidades com barras) na camada 1, com banco, mas a gestão de necessidades (RF-13), que cria esses dados, está na camada 2. Com só a camada 1 pronta, essas duas telas não teriam necessidades reais para mostrar | Na camada 1, as necessidades existem no banco e são criadas só pela carga de dados de demonstração (RF-32); lista e página da ONG as mostram com banco. A tela de gestão (RF-13) continua na camada 2 |
| A-02 | `requirements.md` §8 (legenda de prioridade) × `project-plan.md` §1 | A legenda diz "M = obrigatório para a apresentação", mas depois de D-28 vários requisitos M (RF-08, 13–17, 21, 22, 24, 26) só precisam estar em mock; com banco, entram "se houver tempo" | Coluna "Prior." trocada por "Camada" (1 a 3 ou D), com a legenda do plano |
| A-03 | `requirements.md` RN-15 e RF-19 | A distância é "entre as localidades da ONG e da oferta", mas a oferta não tem localidade própria: só a do agricultor (RF-33) e um local de retirada em texto livre | A oferta tem localidade própria, já preenchida com a do agricultor e alterável por ele; a distância usa a localidade da oferta |

## 2. Duplicidades encontradas

| ID | Onde | Duplicidade | Ação tomada |
|---|---|---|---|
| A-04 | `requirements.md` §14 (Tipo de ajuda: "itens, dinheiro ou voluntariado") × RF-13 e §14 (Necessidade: "itens, voluntários ou dinheiro") | O mesmo conceito com dois nomes ("voluntariado" e "voluntários"), que tende a virar dois campos diferentes no código | Usar um só conjunto de valores: **itens, dinheiro, voluntariado**, tanto no tipo de ajuda da ONG quanto no tipo da necessidade |

## 3. Requisitos ou itens órfãos

| ID | Item | Por que estava órfão | Resolução |
|---|---|---|---|
| A-05 | Lista de localidades (P-06, "mantida pelo administrador") | Não há requisito que diga como ela entra no sistema nem quem a mantém; o plano não a cita | Formalizar como parte de RF-33: a lista vem da carga de dados (RF-32) e o administrador a edita pelo admin do Django. Sem tela própria (coerente com P-11) |

Verificação inversa: todo requisito RF-01 a RF-35 aparece na tabela "Requisitos x MVP" do plano, e todo marco do roadmap remonta a uma camada. Nenhum outro órfão encontrado.

## 4. Decisões sem justificativa identificadas

| ID | Decisão | Problema | Correção |
|---|---|---|---|
| A-06 | `requirements.md` §6: "Agricultor(a) … usa principalmente o celular" | Foi inferência minha ao redigir, não algo dito na entrevista | Trocar por "pode usar o celular (D-23)" |
| A-07 | `requirements.md` §8: "reserva de 1 até o saldo" | O "1" sugere quantidade inteira, mas isso nunca foi decidido | Ver caso extremo E-01 |

## 5. Casos extremos levantados nesta fase

Todos aprovados pelo usuário em 14/10/2026 e incorporados ao `requirements.md` como RN-16 a RN-25 (E-10 foi incorporado ao RF-31).

| ID | Cenário de borda | Comportamento acordado | Requisito afetado |
|---|---|---|---|
| E-01 | Quantidades fracionadas (ex.: 12,5 kg) | Ofertas, reservas e recebimentos aceitam até uma casa decimal em kg; em unidades, só inteiros | RF-18, RF-20, RF-23 |
| E-02 | ONG confirma recebimento maior que o reservado | Recusado: o recebido vai de 0 até a quantidade reservada | RF-23 |
| E-03 | ONG confirma recebimento de 0 | Equivale a "não recebido": a reserva é encerrada sem contar no painel e a quantidade volta ao saldo, se a oferta ainda não venceu | RF-23 |
| E-04 | Oferta vence ("colher até") com reservas ainda não recebidas | As reservas continuam válidas até a ONG confirmar ou cancelar; só o saldo não reservado sai da lista | RF-20, P-03 |
| E-05 | Administrador desativa uma ONG com reservas ativas | As reservas ativas dela são canceladas e as quantidades voltam ao saldo das ofertas | RN-01, RN-14 |
| E-06 | ONG pendente ou reprovada faz login | Entra só na "Minha conta", vê a situação do cadastro (e o motivo, se reprovada) e edita o perfil; não vê ofertas nem cria necessidades | RF-11, RN-01 |
| E-07 | Necessidade atinge a meta | A barra fica em 100% e a necessidade passa a "atendida"; deixa de aceitar novas promessas e inscrições. A ONG pode reabrir aumentando a meta | RF-06, RF-13 |
| E-08 | Visitante vê o local de uma oferta | Vê só o nome da localidade; o texto do local de retirada aparece apenas para ONGs e, como o contato, só depois da reserva para a ONG que reservou | RF-27, RF-28 |
| E-09 | Mês do gráfico "kg por mês" | Conta pela data do recebimento, não da publicação nem da reserva | RF-30 |
| E-10 | Com só a camada 1 pronta, "Impacto por ODS" | Mostra só as reservas de colheita recebidas, já que é a única ação confirmada existente; a carga de dados garante números variados por ODS | RF-31, RN-07 |
| E-11 | ONG fictícia da carga de dados precisa de CNPJ | A carga gera CNPJs com dígitos verificadores válidos e únicos, para não violar RF-10 | RF-32, RF-10 |
| E-12 | Conta com perfis de doador e agricultor clica em "Colheita Solidária" | Cai em publicar oferta (perfil agricultor tem precedência), com um link para ver a lista de ofertas | D-26 |

## 6. Alterações em documentos anteriores

### Já aprovadas pelo usuário

| Documento | Alteração | Motivo |
|---|---|---|
| `project-plan.md` §1 | Camada 1 inclui o model de necessidades, alimentado só pela carga de dados | A-01 |
| `requirements.md` RF-18, RF-19, RN-15, glossário | Oferta ganha localidade própria, preenchida com a do agricultor | A-03 |

### Aprovadas em 14/10/2026, depois da primeira rodada

| Documento | Alteração | Motivo |
|---|---|---|
| `requirements.md` §8 | Coluna "Prior." virou "Camada" (1–3 ou D), com legenda | A-02 |
| `requirements.md` §14 e RF-13 | Valores únicos: itens, dinheiro, voluntariado | A-04 |
| `requirements.md` RF-33 | Lista de localidades vem da carga de dados e é editada no admin do Django | A-05 |
| `requirements.md` §6 | "usa principalmente o celular" → "pode usar o celular (D-23)" | A-06 |
| `requirements.md` §10, RF-31, RF-32 | Novas regras RN-16 a RN-25; RF-31 e RF-32 ajustados | Seção 5, A-01 |
| `requirements.md` apêndice | Notas em D-08, D-16 e D-20 indicando onde foram superadas | Evitar leitura do registro histórico como decisão vigente |
| `requirements.md` §12 | Restrição de equipe menciona o backend concentrado em Jimmie | Coerência com `project-plan.md` §0 |
| `project-plan.md` §1 | Camada 1 inclui as necessidades criadas pela carga de dados | A-01 |

## 7. Conclusão da análise

- **Conflitos:** 3 encontrados (A-01 a A-03), todos resolvidos com o usuário.
- **Duplicidades:** 1 (A-04), resolvida.
- **Órfãos:** 1 (A-05), formalizado. A verificação inversa (plano → requisitos) não achou outros.
- **Decisões sem justificativa:** 2 (A-06, A-07), corrigidas.
- **Casos extremos:** 12 (E-01 a E-12), todos com comportamento acordado e registrado.

A cadeia Objetivos → Requisitos → Casos de uso → Plano está íntegra: todo RF cita um objetivo, decisão ou trecho do PDF; todo RF tem camada no plano; todo marco do roadmap remonta a uma camada. Não há item "a confirmar" vigente nos três documentos (os do apêndice estão marcados como superados). Pronto para a Fase 4.

---
**Status da fase**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 15/10/2026
