# Arquitetura — SustentAgro 2.0

> Documento da Fase 4 (Design). Consolida os ADRs em `adr/` e segue as fronteiras do `CONTEXT.md`.

## 1. Visão geral

Monólito Django 5.2 que gera o HTML no servidor, dividido em apps por área (ADR-001). Roda em container atrás do Nginx da VPS, com PostgreSQL próprio; na máquina dos devs, roda com `runserver` e SQLite (ADR-003). As telas nascem com dados mock que usam os nomes de campo definitivos, e o backend substitui os mocks por camadas sem mexer nos templates (ADR-004, D-28).

## 2. Componentes

| Componente | Responsabilidade | ADR relacionado |
|---|---|---|
| `core` | Settings, URLconf raiz, `base.html` (menu por perfil, rodapé), componentes parciais, CSS comum, página inicial (RF-01 a RF-03), seção "Sobre" (RF-34), mixins de perfil | ADR-001, ADR-002, ADR-005 |
| `contas` | `Usuario`, `PerfilPessoa`, `Localidade`; cadastro por perfil, login e logout, "Minha conta" de pessoa, troca de perfil (RF-07 a RF-09, RF-33, RF-08) | ADR-002 |
| `ongs` | `Ong`, `Ods`, `Necessidade`; cadastro e aprovação de ONG com validação de CNPJ, perfil da ONG, lista com filtros, página da ONG, gestão de necessidades (RF-04 a RF-06, RF-10 a RF-13, RF-35) | ADR-001 |
| `colheita` | `Oferta`, `Reserva`; publicar, listar com distância e visibilidade, reservar, confirmar recebimento, cancelar, "Minhas ofertas" (RF-18 a RF-25, RF-27, RF-28) | ADR-003 |
| `doacoes` | Promessa de itens, inscrição de voluntário, doação em dinheiro, confirmação pela ONG, "Minhas contribuições" (RF-14 a RF-17, RF-26). Camada 2 | ADR-001 |
| `painel` | Indicadores, gráfico de kg por mês e fatia por ODS, calculados por consultas de agregação (RF-29 a RF-31) | ADR-005 |
| Carga de dados | Comando `manage.py carregar_demo`, que apaga e recria localidades, ONGs, pessoas, necessidades, ofertas e ações fictícias (RF-32, RN-24) | — |
| Admin do Django | Aprovar, reprovar e desativar ONGs (ações do admin que chamam `ongs.services`), manter localidades e cadastros (RN-14, RN-19, P-11) | ADR-002 |
| Infraestrutura | `Dockerfile`, `compose.yaml` (app + db), site do Nginx, backup, CI | ADR-006 |

**Regras de negócio** ficam em `services.py` de cada app (por exemplo, `colheita.services.reservar_oferta`, `confirmar_recebimento`, `ongs.services.desativar_ong`). Views e ações do admin só chamam essas funções, e os testes as exercitam diretamente.

**Dependências entre apps:** `core` ← `contas` ← `ongs` ← `colheita`, `doacoes` ← `painel` (o `painel` só lê). Os models devem ser criados nessa ordem.

## 3. APIs e contratos

N/A como API: não há outro consumidor além das próprias páginas, tudo roda num único processo, e não existe JSON exposto.

O contrato que importa é entre **view e template**: cada template recebe objetos com os nomes de campo do modelo de dados da Fase 4a, tanto em mock quanto com banco (ADR-004). Campos calculados (`saldo`, `distancia_km`, `percentual`) têm o mesmo nome nos dois casos.

Se RF-35 for feito, a consulta de CNPJ chama uma API pública gratuita com tempo limite curto (5 s). Qualquer erro é tratado como "CNPJ não confirmado" (RNF-07, D-18).

## 4. Modelo de dados

PostgreSQL 18 em produção e SQLite local (ADR-003). Entidades principais, que serão detalhadas no diagrama da Fase 4a:

| App | Entidades |
|---|---|
| `contas` | `Usuario` (tipo: pessoa ou ONG), `PerfilPessoa` (é doador, é agricultor, telefone, localidade), `Localidade` (nome, latitude, longitude) |
| `ongs` | `Ods` (os 6 do catálogo), `Ong` (CNPJ, situação: pendente, ativa, reprovada ou desativada; motivo; ODS; tipos de ajuda aceitos; localidade; contato; chave Pix; famílias por mês; imagens), `Necessidade` (tipo, unidade, meta, situação) |
| `colheita` | `Oferta` (agricultor, categoria, produto, quantidade, unidade, colher até, localidade, estado, destino doar ou vender, preço, local de retirada, transporte, ONG de destino, data em que abre para todas, situação), `Reserva` (oferta, ONG, quantidade, situação, quantidade recebida, data do recebimento) |
| `doacoes` | `PromessaItens`, `InscricaoVoluntario`, `DoacaoDinheiro` (com a situação de cada uma: prometida ou inscrita, confirmada, recusada, cancelada) |

Decisões que valem para todos: `saldo` é calculado, não guardado (RN-03); quantidades são `Decimal` com uma casa, e inteiras para unidades (RN-16); datas guardadas em UTC e exibidas no fuso `America/Sao_Paulo`, de modo que "colher até" e o mês do gráfico (RN-23) seguem o horário de Brasília.

## 5. Segurança

- **Autenticação:** sessões do Django, login por usuário e senha (RF-09), validadores de senha padrão. Sem recuperação de senha por e-mail: o administrador redefine pelo admin (D-21).
- **Autorização por perfil:** mixins em `core`, aplicados em toda view logada: `LoginRequiredMixin`, `AgricultorRequeridoMixin`, `DoadorRequeridoMixin`, `OngRequeridaMixin` (qualquer situação, para a "Minha conta", RN-20) e `OngAtivaRequeridaMixin` (reservar, criar necessidade, RN-01).
- **Dono dos dados (RNF-05):** toda consulta de edição ou cancelamento filtra pelo dono (`Oferta.objects.filter(agricultor=request.user...)`), e um objeto de outro dono devolve 404. Cada uma dessas views tem um teste.
- **Dados de contato:** telefone e e-mail do agricultor e da ONG, e o texto do local de retirada, só aparecem conforme RF-27 e RN-22. A regra fica num método do model, não no template.
- **Uploads (RNF-06):** só jpeg, jpg, png e webp, até 10 MB, validados no formulário e no model, com nome trocado por UUID (padrão já existente).
- **Segredos (RNF-04):** `SECRET_KEY` e senhas do banco só no `.env`, fora do Git, com um `.env.example` sem segredos. `DEBUG=False`, cookies seguros e HTTPS em produção.
- **Admin:** em `/admin/`, apenas para usuários `is_staff` do grupo.
- **Proteções do Django** mantidas: CSRF em todo formulário, escape automático nos templates, ORM sem SQL manual.
- **VPS:** acesso só de Jimmie, sem chave no GitHub (D-30, ADR-006).

## 6. Observabilidade

Reduzida ao tamanho de um trabalho acadêmico sem usuários reais:

- Django e Gunicorn logam na saída padrão, lida com `docker compose logs app` (limite da VPS: 3 arquivos de 10 MB).
- Logs de acesso e erro do Nginx num arquivo próprio do site (`sustentagro.access.log`, `sustentagro.error.log`).
- Erros 500 são percebidos pelos logs e pelos testes manuais antes de cada publicação. Não há alertas nem métricas.
- O servidor já tem scripts que mostram o estado dos containers; adaptá-los a este projeto é opcional.

## 7. Estratégia de testes

| Nível | O que cobre | Quando |
|---|---|---|
| Testes automatizados (Django `TestCase`) | Toda regra de negócio implementada com banco: RN-01, RN-03, RN-12, RN-13, RN-15 a RN-20 e RN-22 a RN-25 na camada 1; RN-02, RN-07 e RN-21 quando a camada 2 entrar. Também a validação de CNPJ (RF-10) e o "dono dos dados" (RNF-05) | Escritos junto com cada item do backlog, pelo mesmo dev; rodados no CI em todo PR |
| Checagens do CI | `manage.py check`, `makemigrations --check` | Todo PR |
| Teste manual de tela | A tela abre, segue o protótipo e funciona com 360 px de largura (RNF-01) | Na revisão de cada PR de tela |
| Roteiro da demonstração | O fluxo da Colheita do início ao fim (critério de aceite geral), executado na VPS | Depois de cada publicação, a partir do M3 |

Telas em mock não têm teste automatizado (RNF-09). Os casos extremos E-01 a E-12 do `analysis-report.md` são o checklist de revisão das regras.

## 8. Deploy e CI/CD

- **Local:** `pip install -r requirements.txt`, `.env` com `DEBUG=True` e sem `DB_NAME` (SQLite), `migrate`, `carregar_demo`, `runserver`.
- **Produção:** uma pasta própria no servidor, com containers `app` (Gunicorn, uma porta local reservada) e `db` (PostgreSQL 18, rede interna). O Nginx do host atende o subdomínio próprio do projeto com certificado próprio, serve `/static/` e `/media/` do disco e faz `proxy_pass` do resto. O DNS fica no provedor de DNS em modo "Somente DNS" (D-22, P-08). Backup diário pelo script da VPS.
- **Publicação:** manual, só por Jimmie, no fim de cada marco. A primeira é no M2, ainda com mock (R-03). Nada é publicado no dia da apresentação.
- **CI:** GitHub Actions em cada PR (check, migrations, testes no PostgreSQL). Sem CD.
- **Fluxo de código:** um branch por item do backlog e um PR pequeno por tela ou regra. Jimmie revisa e aprova só PR com o CI verde. O `main` é protegido.

## 9. ADRs desta fase

| ADR | Título | Status |
|---|---|---|
| [ADR-001](adr/ADR-001-monolito-django-apps-por-area.md) | Monólito Django com templates no servidor, dividido em apps por área | Aceito |
| [ADR-002](adr/ADR-002-usuario-customizado-e-perfis.md) | Modelo de usuário próprio desde o início, com perfis ligados a ele | Aceito |
| [ADR-003](adr/ADR-003-banco-postgres-sqlite-e-concorrencia.md) | PostgreSQL na VPS, SQLite local e reserva protegida por transação | Aceito |
| [ADR-004](adr/ADR-004-telas-mock-com-contrato-de-campos.md) | Telas mock com os mesmos nomes de campo dos models | Aceito |
| [ADR-005](adr/ADR-005-bootstrap-5-por-cdn.md) | Bootstrap 5 por CDN como único framework de CSS | Aceito |
| [ADR-006](adr/ADR-006-deploy-docker-vps-e-ci.md) | Deploy manual em Docker na VPS e testes automáticos no GitHub Actions | Aceito |

## 10. Cobertura de requisitos não funcionais

| RNF | Como é atendido | ADR relacionado |
|---|---|---|
| RNF-01 Celular | Grade responsiva do Bootstrap 5; teste manual com 360 px em cada PR de tela | ADR-005 |
| RNF-02 Containers na VPS | `compose.yaml` com app em uma porta local reservada e PostgreSQL em rede interna; nada no host | ADR-006, ADR-003 |
| RNF-03 Estáticos pelo Nginx | `collectstatic` + `media/` montados do host e servidos pelo Nginx; WhiteNoise removido | ADR-006 |
| RNF-04 Segredos | `.env` fora do Git, `.env.example`, `DEBUG=False` em produção | ADR-006 |
| RNF-05 Dono dos dados | Mixins de perfil e consultas filtradas pelo dono, com 404 para dados de outro; testes por view | ADR-002 |
| RNF-06 Uploads | Validação de extensão e de tamanho (10 MB) no formulário e no model; nome UUID | — (padrão já existente) |
| RNF-07 Falha da API de CNPJ | Tempo limite e erro tratado como "não confirmado"; só se RF-35 for feito | — (§3) |
| RNF-08 Backup | Script padrão da VPS, com cron próprio | ADR-006 |
| RNF-09 Testes | `TestCase` para cada regra com banco; CI em todo PR contra PostgreSQL | ADR-006, ADR-001 |
| RNF-10 Português | `LANGUAGE_CODE = 'pt-br'`, todos os textos em pt-BR, fuso `America/Sao_Paulo` | — |
| RNF-11 Isolamento do outro projeto do servidor | Diretório, `compose.yaml`, rede, volume, porta, site do Nginx e certificado próprios; conferência do outro projeto do servidor após cada publicação | ADR-006 |

---
**Status**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 15/10/2026
