# Plano de Projeto — SustentAgro 2.0

> Documento vivo da Fase 2 (Planejamento). Parte do `requirements.md` aprovado em 13/10/2026.

## 0. Equipe e capacidade

| Informação | Valor | Origem |
|---|---|---|
| Prazo | Apresentação planejada para 10/11/2026 (P-10); 4 semanas a partir de 13/10/2026 | requirements.md |
| Pessoas programando | 4, todas do grupo Desenvolvimento, que divide backend e frontend | D-29 (revisa D-20) |
| Scrum master | Jimmie Haskell: conduz o processo, auxilia os três grupos (inclusive no código) e revisa os pull requests | D-29 |
| Nomes por grupo | Ver tabela "Grupos" abaixo | Entrevista, 15/10/2026 |
| Experiência do grupo Desenvolvimento | Os 4 já usaram Python e HTML/CSS; experiência com Django desconhecida, então o plano assume que é nenhuma | Entrevista, 15/10/2026 |
| VPS | Só Jimmie acessa (servidor particular e profissional); o projeto fica lá só até a aprovação na matéria | D-30 |
| Entrega para o grupo Plataforma | Novo PDF `SustentAgro_2.0_Projeto.pdf`, detalhando o que o sistema terá e fará e como vai funcionar, com imagens das telas; depois, fotos e vídeos do sistema funcionando | D-30 |

### Grupos (entrevista, 15/10/2026)

| Grupo | Pessoas | Responsabilidade |
|---|---|---|
| Apresentação | Caio Vinício Nunes Vilarouca, Brayan Aragão Pletsch | Presença, apresentação e relatório com o professor avaliador |
| Plataforma | João Matheus Bezerra, Guilherme de Melo Lucas, João Vitor de Freitas Silva, Vitor Gomes Araújo | Preencher os dados no DreamShaper, respondendo às perguntas específicas da plataforma |
| Desenvolvimento | Vinicius Pereira Souza, Júlia Sernagiotto Barbosa, Gabriel Ribeiro de Carvalho, Pedro Freire de Farias | Codificar o sistema: backend e frontend |
| Scrum master | Jimmie Haskell Gonçalves da Silva | Coordena e auxilia os três grupos |

**Consequência para o plano (revisada em 15/10/2026, D-29):** o gargalo agora é a capacidade total. As mesmas 4 pessoas, sem experiência presumida em Django, fazem as telas mock e depois a camada 1 com banco. O plano precisa (a) entregar a elas um padrão pronto (esqueleto, `base.html`, um exemplo de tela e de view) para que aprendam Django copiando, (b) começar pelo que já sabem (HTML/CSS das telas) e só depois passar a views e models, e (c) manter a ordem das camadas para que o mais importante fique pronto primeiro, caso o tempo acabe. Jimmie monta o esqueleto, cuida sozinho da VPS e acompanha de perto as partes de regra de negócio da Colheita.

## 1. MVP

### Estratégia de entrega (D-28)

1. **Telas primeiro.** Todas as telas (as 7 do PDF e as da área logada) ficam prontas e navegáveis com dados fictícios fixos (mock), já servidas pelo Django com as URLs definitivas.
2. **Backend depois, por camadas.** O backend substitui os mocks na ordem abaixo. Cada tela trocada de mock para dados reais mantém a mesma aparência; quem fez a tela só ajusta o que mudar.
3. **Protótipo como referência.** Antes de o grupo começar os templates, a Fase 4b gera um protótipo navegável de todas as telas (inclusive versão celular), usado como modelo de visual e de componentes, não como código para copiar.

O MVP da apresentação é: **todas as telas em mock + camada 1 com banco**. As camadas 2 e 3 entram se houver tempo, nessa ordem.

### Camadas do backend

| Camada | Conteúdo | Requisitos | Situação na apresentação |
|---|---|---|---|
| 0 — Telas mock | Todas as telas navegáveis com dados fictícios fixos, responsivas | Visual de todos os RF | **Obrigatória** |
| 1 — Núcleo | Cadastro, login e aprovação de ONG; localidades; busca, lista e página da ONG; Colheita Solidária completa; painel de impacto; dados de demonstração, incluindo as necessidades das ONGs (só pela carga; a tela de gestão é da camada 2, A-01) | RF-01, 02, 04–07, 09–12, 18–20, 23, 25, 27–33 | **Obrigatória com banco** |
| 2 — Doações | Necessidades, promessa de itens, voluntariado, doação em dinheiro, confirmação pela ONG, "minhas contribuições" | RF-13–17, 26 | Com banco se houver tempo; senão, mock |
| 3 — Refinamentos | Oferta direcionada (48 h), selo "urgente", acúmulo de perfis, cancelamentos | RF-08, 21, 22, 24 | Com banco se houver tempo; senão, mock |
| Desejáveis | Carrossel, seção "Sobre", consulta externa de CNPJ | RF-03, 34, 35 | Só com folga |

Ordem de corte se faltar tempo: desejáveis → camada 3 → camada 2. A camada 0 e a camada 1 não são cortadas.

### Requisitos x MVP

| Requisito | Tela mock (camada 0) | Com banco no MVP? | Justificativa |
|---|---|---|---|
| RF-01, 02, 04, 05, 06 | Sim | Sim (camada 1) | Telas 01–03; consultas simples, baratas no servidor |
| RF-03 | Sim | Não (desejável) | Desejável na Fase 1 |
| RF-07, 09, 10, 11, 12 | Sim | Sim (camada 1) | Sem conta e ONG aprovada não há fluxo da Colheita |
| RF-08 | Sim | Não (camada 3) | Acúmulo de perfis não é necessário para demonstrar nenhum fluxo |
| RF-13, 14, 15, 16, 17, 26 | Sim | Não (camada 2) | Fluxos de doação ficaram como "se houver tempo" (D-28). As necessidades em si existem no banco desde a camada 1, criadas pela carga de dados (A-01) |
| RF-18, 19, 20, 23, 25, 27, 28 | Sim | Sim (camada 1) | Fluxo da Colheita, mínimo obrigatório (D-28) |
| RF-21, 22, 24 | Sim | Não (camada 3) | Enriquecem a Colheita, mas o fluxo se demonstra sem elas |
| RF-29, 30, 31 | Sim | Sim (camada 1) | O painel fecha o fluxo da Colheita (OBJ-04) |
| RF-32 | — | Sim (camada 1) | Sem dados de demonstração o painel e as listas ficam vazios |
| RF-33 | Sim | Sim (camada 1) | Distância da tela 06 depende das localidades |
| RF-34 | Sim | Não (desejável) | Desejável na Fase 1 |
| RF-35 | — | Não (desejável) | Desejável na Fase 1 (D-27) |

## 2. Roadmap

Quatro semanas, de 13/10 a 10/11/2026 (P-10).

| Marco | Período | Jimmie (scrum master) | Desenvolvimento | Plataforma e Apresentação | Depende de |
|---|---|---|---|---|---|
| M0 — Pré-projeto | 14 a 17/10 | Aprovar Fases 2 a 4b e o novo PDF | Ler os documentos e o protótipo | Receber o novo PDF (17/10) e começar o DreamShaper | Aprovação de cada fase |
| M1 — Esqueleto | até 19/10 | Rotas e views de todas as telas com dados mock; `base.html`; uma tela-exemplo completa como padrão; repositório com os 4 como colaboradores | Preparar o ambiente (Python, Git, rodar o projeto local) | Preencher o DreamShaper com o PDF | M0 |
| M2 — Telas mock | 19 a 26/10 | Revisar PRs (Docker e primeira publicação já feitos em 17/10) | Montar todas as telas sobre o esqueleto, seguindo o protótipo; versão celular. No fim, models da camada 1 com o apoio de Jimmie | Continuar o DreamShaper | M1 |
| M3 — Colheita real | 27/10 a 02/11 | Acompanhar as regras da Colheita (saldo, reserva, recebimento); publicar na VPS; revisar PRs | Camada 1 com banco: cadastro/login, localidades, Colheita, painel, dados de demonstração | Primeiras fotos das telas publicadas | M2 |
| M4 — Extras e ensaio | 03 a 08/11 | Publicar; revisar PRs | Camada 2, depois camada 3, até 07/11; gravar os vídeos do fluxo da Colheita | Fotos e vídeos no DreamShaper; relatório; ensaio da apresentação | M3 |
| Congelamento | 08 e 09/11 | Última publicação até 09/11 | Só correção de defeitos | Ensaio final | M4 |
| Apresentação | 10/11 | — | — | Apresentação ao avaliador | — |

### Situação em 17/10/2026

| Marco | Situação |
|---|---|
| M0 · Pré-projeto | Concluído em 17/10 (fases 1 a 4b, protótipo e PDF do projeto) |
| M1 · Esqueleto | Concluído em 17/10, dois dias antes do previsto (BL-01 a BL-08) |
| Primeira publicação (BL-10, previsto para o M2) | Concluída em 17/10, já com publicação automática a cada merge na branch `prod` |
| M2 · Telas mock | Começa em 19/10, como previsto |

**Decisão (17/10/2026):** as datas dos marcos não mudam. Os dois dias ganhos no M1 e a publicação já feita viram margem para o grupo Desenvolvimento, que não tem experiência prévia em Django (R-01).

## 3. Releases

- A primeira publicação na VPS acontece no M2, ainda com as telas mock, para que a implantação do Django, que nunca foi testada nessa VPS, seja validada cedo.
- Depois disso, uma publicação ao fim de cada marco (M2, M3 e M4) e a última até 09/11.
- Nada é publicado no dia da apresentação.

## 4. Priorização

Critérios, nesta ordem:

1. **O que destrava outras pessoas vem antes.** O esqueleto de rotas e views mock (M1) vem antes de tudo, porque sem ele o grupo não começa os templates.
2. **O mínimo obrigatório da apresentação vem antes do opcional.** Telas mock e camada 1 antes das camadas 2 e 3 (D-28).
3. **Risco técnico alto vem cedo.** A implantação na VPS é feita no M2, não no fim.
4. **Dentro de uma camada, o que outros requisitos usam vem antes.** Contas, perfis e localidades antes de ofertas; ofertas antes de reservas; reservas antes do painel.

| Item | Prioridade | Critério aplicado |
|---|---|---|
| Esqueleto de rotas e views mock | 1 | 1 |
| Telas mock de todo o site | 2 | 2 |
| Publicação na VPS | 3 | 3 |
| Contas, perfis, aprovação, localidades | 4 | 2, 4 |
| Ofertas, reservas, recebimento | 5 | 2, 4 |
| Painel de impacto e dados de demonstração | 6 | 2, 4 |
| Camada 2 | 7 | 2 |
| Camada 3 | 8 | 2 |
| Desejáveis | 9 | 2 |

## 5. Dependências

### Forma de trabalho do grupo (entrevista, 14/10/2026)

- **Repositório:** novo, criado por Jimmie no GitHub; os demais entram como colaboradores. O repositório da versão 1 (`github.com/BrayanPletsch/SustentAgro`) fica só como histórico.
- **Fluxo:** cada pessoa trabalha num branch e abre um pull request; Jimmie revisa e aprova antes de entrar no `main`.

| Dependência | Tipo | Responsável | Prazo | Impacto se atrasar |
|---|---|---|---|---|
| Aprovação das Fases 2, 3, 4, 4a e 4b (todas aprovadas; 4a e 4b em 16/10/2026) | Decisão | Jimmie | 17/10 (feito) | Sem protótipo e sem modelo de dados, o esqueleto e as telas atrasam |
| Repositório novo com todos como colaboradores | Sistema | Jimmie | 18/10 | O grupo não consegue começar em 19/10 |
| Nomes e experiência do grupo | Decisão | Jimmie, com o grupo | 15/10 (feito) | — |
| Novo PDF do projeto: parte para o DreamShaper e guia de navegação dos documentos para os devs (D-31) | Equipe | Claude, com aprovação de Jimmie | 17/10, junto com o protótipo | O grupo Plataforma não começa a preencher |
| Fotos e vídeos do sistema funcionando | Equipe | Desenvolvimento, com Jimmie | Fotos no M3; vídeos no M4 | O DreamShaper fica sem as mídias pedidas |
| Esqueleto de rotas e views mock (M1) | Equipe | Jimmie | 19/10 | Todo o frontend espera |
| Protótipo navegável (Fase 4b) | Equipe | Claude, com aprovação de Jimmie | 17/10 | O grupo monta telas sem referência visual comum |
| Subdomínio no provedor de DNS e certificado | Sistema | Jimmie | 26/10 (M2) | Sem publicação na VPS, o risco de implantação fica para o fim |
| Revisão de pull requests | Equipe | Jimmie | Contínuo | Trabalho do grupo parado esperando revisão |
| Data exata da apresentação | Decisão | Avaliador | Assim que divulgada | O roadmap assume 10/11 (P-10) |

## 6. Riscos

| ID | Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|---|
| R-01 | Os 4 devs, sem experiência presumida em Django, não terminam telas mock e camada 1 a tempo | Alta | Alto | Telas mock primeiro (D-28), começando pelo HTML/CSS que já sabem; esqueleto e tela-exemplo prontos no M1 para copiar; backend em camadas com ordem de corte; só a camada 1 é obrigatória com banco |
| R-02 | Revisão de pull requests por uma só pessoa (Jimmie, que também coordena os três grupos) trava o Desenvolvimento | Média | Médio | Pull requests pequenos, um por tela; um horário fixo de revisão por dia; cada tela em arquivos próprios para reduzir conflitos; regras de revisão objetivas (a tela abre, segue o protótipo, funciona no celular) |
| R-03 | Implantação do Django na VPS, que nunca foi testada lá, falha ou demora | Média | Alto | Primeira publicação no M2, ainda com mock, seguindo o roteiro "Como adicionar um novo projeto" da documentação da VPS |
| R-04 | Várias pessoas editando `base.html` e o CSS comum geram conflitos e visual inconsistente | Média | Médio | `base.html`, menu e estilos comuns ficam prontos no M1 e têm um único responsável; as telas só usam esses componentes |
| R-05 | Os dados mock não batem com os dados reais e as telas precisam ser refeitas na troca | Média | Médio | Os dados mock usam exatamente os nomes de campos do modelo de dados da Fase 4a; a troca de mock para real muda a view, não o template |
| R-06 | Regras de negócio da Colheita (saldo, reservas, recebimento, painel) ficam com quem nunca usou Django e saem erradas | Média | Alto | Tarefas do backlog em ordem de dificuldade; as de regra de negócio em dupla ou com acompanhamento de Jimmie; casos extremos E-01 a E-12 como checklist de revisão |
| R-07 | O pré-projeto passa de 17/10 e atrasa o esqueleto | Média | Alto | Fases 3 a 4b conduzidas com poucas perguntas, já que a maior parte das decisões foi tomada na Fase 1 |
| R-08 | A publicação do SustentAgro afeta o outro projeto do servidor em produção | Baixa | Alto | `compose.yaml`, banco, rede, porta e site do Nginx próprios (RNF-11); conferência do outro projeto do servidor após cada publicação |
| R-09 | A VPS ou a internet falha no dia da apresentação | Baixa | Alto | Ter o projeto rodando localmente no notebook da apresentação, com os mesmos dados de demonstração |

## 7. KPIs

N/A como indicadores pós-lançamento: o projeto não terá usuários reais (Fase 1, seção 3), então não há uso a medir.

Em seu lugar, três indicadores de andamento, acompanhados semanalmente por Jimmie:

| Indicador | Meta | Como medir |
|---|---|---|
| Telas mock prontas | 100% até 26/10 | Telas no `main` que abrem e seguem o protótipo ÷ total de telas do backlog |
| Requisitos da camada 1 com banco | 100% até 02/11 | Requisitos da camada 1 cujo critério de aceite passa com dados reais ÷ total da camada 1 |
| Pull requests esperando revisão há mais de 24 h | 0 | Lista de pull requests abertos no GitHub |

## 8. Critérios de sucesso

O projeto é um sucesso se, em 10/11/2026:

1. Todas as telas estão publicadas no subdomínio da VPS, em HTTPS, navegáveis em computador e celular.
2. O fluxo da Colheita roda com banco do início ao fim na frente do avaliador, sem tocar no banco à mão.
3. O painel de impacto mostra números que mudam quando o fluxo da Colheita é executado.
4. A apresentação liga o que foi construído aos ODS 2, 8 e 10 e à fundamentação em Gramsci e Adorno.
5. O outro projeto do servidor continua funcionando normalmente.

A distribuição de tarefas por pessoa é feita no `backlog.md` da Fase 4, depois do levantamento de nomes e experiência.

---
**Status da fase**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 14/10/2026 (ajustado na Fase 3, A-01; revisado e reaprovado em 15/10/2026 por D-29 e D-30)
