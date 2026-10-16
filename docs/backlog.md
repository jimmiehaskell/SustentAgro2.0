# Backlog — SustentAgro 2.0

> Documento da Fase 4 (Design). Traduz requisitos e arquitetura em itens executáveis, com responsável e marco (`project-plan.md` §2). Último artefato desta fase.

## Como ler

- **Camada:** 0 = tela mock; 1 = obrigatória com banco; 2 e 3 = com banco se houver tempo; D = desejável; Infra = infraestrutura e processo (`project-plan.md` §1).
- **No MVP?** Sim = camada 0, camada 1 ou infraestrutura necessária para a apresentação (D-28).
- **Prioridade:** 1 é a mais alta, seguindo os critérios do `project-plan.md` §4.
- Todo item de camada 1, 2 ou 3 inclui os **testes automatizados** das regras que implementa (RNF-09), escritos pelo mesmo responsável.
- Cada item vira **um branch e um PR**; itens grandes podem virar mais de um PR.

## Divisão por área

A distribuição segue um app por pessoa (ADR-001), para cada uma ficar dona de uma parte do código do começo ao fim. Como a experiência individual é desconhecida (todos sabem Python e HTML/CSS), a divisão é uma proposta: Jimmie pode trocar as pessoas de área sem mudar o resto do backlog.

| Pessoa | Área (app) | O que leva de mais difícil | Apoio de Jimmie |
|---|---|---|---|
| Vinicius | `contas`: cadastro, login, "Minha conta" de pessoa | Cadastro por perfil e cadastro da ONG com CNPJ | Usuário próprio e mixins já vêm prontos do M1 |
| Julia | `ongs`: Início, lista, página da ONG, perfil da ONG | Filtros combinados e aprovação no admin | — |
| Gabriel Ribeiro | `colheita`: publicar, lista de ofertas, reservas | Reserva com saldo, visibilidade e recebimento: as regras mais delicadas do sistema | **Em dupla** nos itens de reserva e recebimento (R-06) |
| Pedro Freire | `painel` e `doacoes`, carga de dados, "Minhas ofertas" | Consultas do painel e carga de dados coerente | — |
| Jimmie | `core`, infraestrutura, revisão | Esqueleto, deploy na VPS | — |

## Itens

### M1 — Esqueleto (até 19/10) · Jimmie

| ID | Item | Descrição | Origem | Responsável | Camada | Prioridade | No MVP? |
|---|---|---|---|---|---|---|---|
| BL-01 | Repositório novo | Repositório no GitHub com os 4 devs como colaboradores, `main` protegido (só por PR aprovado e com o CI verde), modelo de PR com o checklist de revisão | `project-plan.md` §5, R-02 | Jimmie | Infra | 1 | Sim |
| BL-02 | Esqueleto do projeto | Apps `core`, `contas`, `ongs`, `colheita`, `doacoes`, `painel`; `contas.Usuario` antes da primeira migration; settings pelo `.env` (SQLite sem `DB_NAME`, PostgreSQL com), `TIME_ZONE = 'America/Sao_Paulo'`, `STATICFILES_DIRS` corrigido; saem WhiteNoise, Tailwind, `package.json` e o `ongs` antigo | ADR-001, ADR-002, ADR-003, ADR-006 | Jimmie | Infra | 1 | Sim |
| BL-03 | Base visual e componentes | `base.html` com Bootstrap 5 e menu por perfil (Cadastrar ou Minha conta/Sair; destino de "Colheita Solidária" conforme D-26 e RN-25), rodapé, `sustentagro.css`; parciais de cartão de ONG, selo de ODS, barra de progresso, cartão de oferta e mensagens | ADR-005, R-04, RF-09 | Jimmie | 0 | 1 | Sim |
| BL-04 | Rotas e views mock | Todas as URLs definitivas, cada view devolvendo dados do `mocks.py` do app, com os nomes de campo da Fase 4a e o comentário `# MOCK: trocar na camada N`; templates vazios com título, para os devs preencherem | ADR-004 | Jimmie | 0 | 1 | Sim |
| BL-05 | Mixins de perfil | `AgricultorRequeridoMixin`, `DoadorRequeridoMixin`, `OngRequeridaMixin`, `OngAtivaRequeridaMixin`, com testes | ADR-002, RNF-05, RN-01, RN-20 | Jimmie | 1 | 1 | Sim |
| BL-06 | Tela-exemplo | A Página da ONG (tela 03) completa em mock, como modelo de template, uso de parciais e responsividade | ADR-004, R-01 | Jimmie | 0 | 1 | Sim |
| BL-07 | CI | GitHub Actions em cada PR: `check`, `makemigrations --check` e testes com PostgreSQL de serviço | ADR-006, RNF-09 | Jimmie | Infra | 1 | Sim |
| BL-08 | Guia do dev | `CONTRIBUTING.md` em pt-BR: instalar, rodar local, criar branch, abrir PR, o que a revisão confere, onde ficam regra (services), mock e template | R-01, R-02 | Jimmie | Infra | 1 | Sim |

### M2 — Telas mock (19 a 26/10)

| ID | Item | Descrição | Origem | Responsável | Camada | Prioridade | No MVP? |
|---|---|---|---|---|---|---|---|
| BL-09 | Ambiente de cada dev | Clonar, criar `.venv`, rodar o projeto local e abrir um PR de teste (por exemplo, o próprio nome na seção "Sobre" do mock) | BL-08 | Vinicius, Julia, Gabriel, Pedro | Infra | 2 | Sim |
| BL-10 | Publicação na VPS | DNS, `Dockerfile`, `compose.yaml`, site do Nginx, certificado, backup e primeira publicação com as telas mock; conferir o outro projeto do servidor | ADR-006, RNF-02, RNF-03, RNF-08, RNF-11, R-03 | Jimmie | Infra | 3 | Sim |
| BL-11 | Tela 04 — Cadastro por perfil | Escolha do perfil e os três formulários (doador/voluntário, agricultor, ONG), com a lista de localidades | RF-07, RF-33, PDF 3.5 | Vinicius | 0 | 2 | Sim |
| BL-12 | Login | Tela de login no visual novo, estendendo o `base.html` | RF-09 | Vinicius | 0 | 2 | Sim |
| BL-13 | Minha conta — pessoa | Página de doador/voluntário com "Minhas contribuições" e troca de perfil | RF-26, RF-08, D-16 | Vinicius | 0 | 2 | Sim |
| BL-14 | Tela 01 — Início | Busca por texto, cartões dos 6 ODS com contagem, carrossel | RF-01, RF-02, RF-03, PDF tela 01 | Julia | 0 | 2 | Sim |
| BL-15 | Tela 02 — Lista de ONGs | Filtros de ODS, tipo de ajuda e cidade; cartão com "Precisa agora"; mensagem de nenhum resultado | RF-04, RF-05, UC-01 | Julia | 0 | 2 | Sim |
| BL-16 | Minha conta — ONG | Situação do cadastro (pendente, reprovada com o motivo, ativa), edição do perfil e lista de necessidades | RF-11, RF-12, RF-13, RN-20 | Julia | 0 | 2 | Sim |
| BL-17 | Tela 05 — Publicar oferta | Formulário completo da oferta, com destino doar ou vender e ONG de destino opcional | RF-18, PDF 3.3 | Gabriel | 0 | 2 | Sim |
| BL-18 | Tela 06 — Ofertas | Versão ONG (distância, filtros de km, botão Reservar com quantidade, selo "urgente") e versão visitante (sem distância, contato ou botão, com convite para cadastro) | RF-19, RF-20, RF-22, RF-28, D-26 | Gabriel | 0 | 2 | Sim |
| BL-19 | Minhas reservas (ONG) | Reservas da ONG com contato do agricultor e o formulário de confirmar recebimento | RF-23, RF-27, RF-24 | Gabriel | 0 | 2 | Sim |
| BL-20 | Tela 07 — Painel de impacto | Quatro indicadores, gráfico de kg por mês (Chart.js), barras por ODS, estado vazio | RF-29, RF-30, RF-31, UC-13 | Pedro | 0 | 2 | Sim |
| BL-21 | Minhas ofertas (agricultor) | Ofertas com saldo, reservas, situação e contato da ONG | RF-25, RF-27 | Pedro | 0 | 2 | Sim |
| BL-22 | Telas de doação | "Quero doar" (itens), "Quero ser voluntário(a)", doação em dinheiro com a chave Pix, confirmação de doações pela ONG | RF-14, RF-15, RF-16, RF-17 | Pedro | 0 | 2 | Sim |
| BL-23 | Seção "Sobre" | Texto do projeto e a lista dos 10 nomes do PDF | RF-34, P-09 | Pedro | D | 9 | Não |

### M2 (fim) e M3 — Camada 1 com banco (até 02/11)

Ordem obrigatória dos models: `contas` → `ongs` → `colheita` (ADR-001). Cada item troca o mock da tela correspondente pelos dados reais.

| ID | Item | Descrição | Origem | Responsável | Camada | Prioridade | No MVP? |
|---|---|---|---|---|---|---|---|
| BL-24 | Models de `contas` | `PerfilPessoa` e `Localidade`, no admin, conforme a Fase 4a | RF-33, RN-12, A-05 | Vinicius | 1 | 4 | Sim |
| BL-25 | Models de `ongs` | `Ods`, `Ong` (situação e motivo, tipos de ajuda, chave Pix, famílias por mês) e `Necessidade`, no admin | RF-11, RF-12, A-01, A-04 | Julia | 1 | 4 | Sim |
| BL-26 | Models de `colheita` | `Oferta` e `Reserva`, saldo calculado, validações de preço e de quantidade | RN-03, RN-13, RN-16, A-03 | Gabriel, com Jimmie | 1 | 4 | Sim |
| BL-27 | Carga de dados de demonstração | Comando `carregar_demo`: localidades do DF e Entorno com coordenadas, ODS, ONGs com CNPJ válido, pessoas, necessidades, ofertas, reservas recebidas espalhadas por meses | RF-32, RN-24, P-06, E-10, E-11 | Pedro | 1 | 4 | Sim |
| BL-28 | Cadastro e login reais | Os três cadastros gravando conta e perfil e já logando; login e logout; menu por perfil | RF-07, RF-09, RF-33, UC-02 | Vinicius | 1 | 4 | Sim |
| BL-29 | Cadastro e aprovação de ONG | Validação de dígitos e unicidade do CNPJ; ONG nasce pendente; ações do admin de aprovar, reprovar com motivo e desativar (cancelando as reservas ativas) | RF-10, RF-11, RN-01, RN-14, RN-19, RN-20, UC-03 | Vinicius (cadastro), Julia (ações do admin) | 1 | 4 | Sim |
| BL-30 | Início, lista e página da ONG reais | Busca, contagem por ODS, filtros combinados, "Precisa agora", necessidades com barra; só ONGs ativas | RF-01, RF-02, RF-04, RF-05, RF-06, RN-01 | Julia | 1 | 5 | Sim |
| BL-31 | Perfil da ONG real | Edição do perfil com upload de imagens validado | RF-12, RNF-06, RNF-05 | Julia | 1 | 5 | Sim |
| BL-32 | Publicar oferta real | Gravação com localidade preenchida pela do agricultor; recusa de venda sem preço e de "colher até" no passado | RF-18, RN-13, RN-16, UC-08 | Gabriel | 1 | 5 | Sim |
| BL-33 | Lista de ofertas real | Visibilidade para ONG ativa e para visitante, distância por haversine, filtros de km, oferta vencida ou sem saldo fora da lista | RF-19, RF-28, RN-05, RN-15, RN-18, RN-22, P-03 | Gabriel | 1 | 5 | Sim |
| BL-34 | Reservar oferta | `reservar_oferta` com transação e trava da linha; recusa acima do saldo; contato liberado após a reserva | RF-20, RF-27, RN-03, UC-09 | Gabriel, em dupla com Jimmie | 1 | 5 | Sim |
| BL-35 | Confirmar recebimento | Quantidade recebida de 0 até a reservada; 0 encerra e devolve ao saldo se a oferta não venceu; data do recebimento | RF-23, RN-17, RN-18, UC-10 | Gabriel, em dupla com Jimmie | 1 | 5 | Sim |
| BL-36 | Minhas ofertas real | Ofertas do agricultor logado com saldo, reservas e contato | RF-25, RF-27, RNF-05 | Pedro | 1 | 5 | Sim |
| BL-37 | Painel real | Kg salvos, famílias, renda, ONGs ativas; kg por mês pela data do recebimento; fatia por ODS das reservas recebidas | RF-29, RF-30, RF-31, RN-07 a RN-11, RN-23, E-10 | Pedro | 1 | 6 | Sim |
| BL-38 | Destino de "Colheita Solidária" | O menu leva cada perfil ao destino certo, com precedência de agricultor | D-26, RN-25 | Vinicius | 1 | 6 | Sim |
| BL-39 | Fotos das telas publicadas | Capturas de cada tela (computador e celular) para o DreamShaper | D-30 | Jimmie, com os 4 devs | Infra | 6 | Sim |

### M4 — Extras e ensaio (03 a 08/11)

| ID | Item | Descrição | Origem | Responsável | Camada | Prioridade | No MVP? |
|---|---|---|---|---|---|---|---|
| BL-40 | Vídeos do sistema | Gravação do fluxo da Colheita do início ao fim e das telas principais, com narração ou legenda | D-30 | Jimmie, com os 4 devs | Infra | 6 | Sim |
| BL-41 | Gestão de necessidades | A ONG cria, edita e encerra; meta menor que o confirmado é recusada; "atendida" ao bater a meta e reabertura ao aumentá-la | RF-13, RN-21, UC-04 | Julia | 2 | 7 | Não |
| BL-42 | Promessa de itens e voluntariado | Promessa e inscrição pendentes, que não movem a barra | RF-14, RF-15, RN-02, UC-05, UC-06 | Vinicius | 2 | 7 | Não |
| BL-43 | Doação em dinheiro | Necessidade em reais ou doação livre; chave Pix exibida; fica prometida | RF-17, UC-07 | Pedro | 2 | 7 | Não |
| BL-44 | Confirmação pela ONG | A ONG confirma com quantidade ou valor, ou recusa; a barra avança; ações contam no painel | RF-16, RN-02, RN-07 | Pedro | 2 | 7 | Não |
| BL-45 | Minhas contribuições real | Lista do doador com situação e cancelamento das não confirmadas | RF-26, P-07 | Vinicius | 2 | 7 | Não |
| BL-46 | Oferta direcionada e selo "urgente" | 48 h só para a ONG de destino; selo e topo da lista depois de 48 h abertas a todas | RF-21, RF-22, RN-04, RN-06, P-05 | Gabriel | 3 | 8 | Não |
| BL-47 | Cancelamentos | ONG ou agricultor cancela reserva não recebida; agricultor cancela oferta sem reservas ativas | RF-24, UC-09, UC-11 | Gabriel | 3 | 8 | Não |
| BL-48 | Acúmulo de perfis | Pessoa ativa o segundo perfil em "Minha conta" | RF-08, RN-12 | Vinicius | 3 | 8 | Não |
| BL-49 | Carrossel real | Carrossel da Início com ONGs ativas | RF-03 | Julia | D | 9 | Não |
| BL-50 | Consulta externa de CNPJ | API pública com tempo limite; falha → "CNPJ não confirmado" | RF-35, RNF-07, D-18 | Vinicius | D | 9 | Não |
| BL-51 | Ensaio da demonstração | Roteiro do fluxo da Colheita executado na VPS com a carga de dados; plano B local pronto | Critérios de aceite gerais, R-09 | Jimmie, com todos | Infra | 6 | Sim |

### Grupos Plataforma e Apresentação

| ID | Item | Descrição | Origem | Responsável | Prazo |
|---|---|---|---|---|---|
| BL-52 | Novo PDF do projeto | `SustentAgro_2.0_Projeto.pdf` em duas partes. **Parte 1, para a Plataforma:** o que o sistema terá e fará e como vai funcionar, com as imagens do protótipo. **Parte 2, guia do desenvolvedor:** passo a passo para navegar pelos documentos do projeto (requisitos, regras de negócio, ADRs, modelo de dados, protótipo, backlog), dizendo onde consultar cada coisa ao implementar um item: por exemplo, para BL-34, abrir RF-20 e RN-03 no `requirements.md`, os casos E-02 a E-04 no `analysis-report.md`, o ADR-003, as entidades `Oferta` e `Reserva` no diagrama e a tela 06 no protótipo | D-30, D-31 | Claude, com aprovação de Jimmie | 17/10 |
| BL-53 | Preenchimento do DreamShaper | Responder às perguntas da plataforma a partir do novo PDF; anexar fotos (M3) e vídeos (M4) | D-30 | João Matheus, Guilherme Lucas, João Vitor, Vitor Gomes | Contínuo, até 09/11 |
| BL-54 | Relatório e apresentação | Relatório para o avaliador e roteiro da apresentação, ligando o sistema aos ODS 2, 8 e 10 e a Gramsci e Adorno | OBJ-04, critério de sucesso 4 | Caio, Brayan | Até 09/11 |

## Notas de priorização

A ordem segue os critérios do `project-plan.md` §4: primeiro o que destrava outras pessoas (M1 inteiro com prioridade 1), depois o mínimo obrigatório (telas mock e camada 1), o risco técnico cedo (publicação na VPS no M2) e, dentro da camada 1, o que outros itens usam (models de `contas` → `ongs` → `colheita`; ofertas antes de reservas; reservas antes do painel).

Carga aproximada por pessoa na camada 0 + camada 1: Vinicius 7 itens, Julia 7, Gabriel 8 (dois em dupla com Jimmie), Pedro 6 (mais a carga de dados, que é grande). Gabriel tem a parte mais delicada; se atrasar, BL-33 e BL-19 são os primeiros a passar para Pedro.

## Itens fora do MVP

BL-23 e BL-41 a BL-50 (camadas 2 e 3 e desejáveis) só entram com banco se houver tempo, nesta ordem de corte: desejáveis → camada 3 → camada 2 (`project-plan.md` §1). As telas correspondentes já existem em mock desde o M2 (BL-13, BL-16, BL-22).

---
**Status**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 15/10/2026

**Ao aprovar este documento**, a Fase 4 está concluída. Seguem a Fase 4a (diagrama do modelo de dados) e a Fase 4b (protótipo navegável), já pedidas no intake, e depois o novo PDF.
