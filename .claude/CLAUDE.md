# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

O SustentAgro 2.0 conecta agricultores familiares, ONGs e pessoas que querem ajudar: o agricultor publica o excedente, as ONGs próximas reservam e confirmam o recebimento, e um painel público mostra o impacto. É um trabalho acadêmico (Itinerário 5), em Django 5.2, desenvolvido por 4 pessoas iniciantes em Django com revisão do scrum master (Jimmie).

Textos de interface, comentários e mensagens de commit são em português do Brasil; mantenha em português todo texto novo.

Os documentos do pré-projeto estão em `docs/` (requisitos com RF/RN/UC, ADRs, backlog BL-01 a BL-54, modelo de dados, protótipo `docs/prototipo.html` e o PDF com o Guia do desenvolvedor). Toda mudança deve remontar a um código desses documentos. A cópia de trabalho completa (com dados do servidor, que **não podem ir para o repositório público**) fica em `.claude/pre-projeto/`, ignorada pelo Git; `docs/` é gerado dela sem os dados do servidor.

## Comandos

```bash
source .venv/Scripts/activate        # Git Bash no Windows
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
python manage.py test                                    # todos os testes
python manage.py test colheita.tests.test_reserva        # um módulo
python manage.py makemigrations --check --dry-run        # o CI falha se faltar migration
```

O CI (`.github/workflows/ci.yml`) roda `check`, `makemigrations --check` e os testes contra PostgreSQL em todo PR.

## Arquitetura

- Monólito Django com templates no servidor, um app por área (ADR-001): `core` (settings, `base.html`, componentes, perfis, mixins, início), `contas` (usuário, perfis, localidades, cadastro, login), `ongs` (ONG, ODS, necessidades), `colheita` (ofertas, reservas), `doacoes` (camada 2), `painel` (só lê).
- `AUTH_USER_MODEL = 'contas.Usuario'`, com `tipo_conta` pessoa/ong (ADR-002). Os demais models ainda não existem: cada `models.py` traz, em comentário, os campos exatos a criar no item do backlog correspondente.
- Banco: SQLite sem `DB_NAME` no `.env`; PostgreSQL com (ADR-003). `TIME_ZONE = 'America/Sao_Paulo'`.
- Telas primeiro em mock (ADR-004): cada view lê `<app>/mocks.py`, cujos objetos usam os mesmos nomes de campo do modelo de dados (`core.mocks_util.obj`/`lista`, que aceita `.all` no template). Views mock têm o comentário `MOCK: trocar na camada N`.
- Regras de negócio só em `<app>/services.py`; views e ações do admin só chamam os serviços. Funções ainda não implementadas levantam `NotImplementedError('BL-xx')`.
- Listas de valores fixos em `<app>/choices.py` (contrato usado por mocks e testes).
- Perfil atual: `core.perfis.perfil_da_requisicao` (em DEBUG, pode ser simulado pela sessão via `/mock/perfil/<perfil>/`). O context processor `core.context_processors.perfil` expõe `perfil`, `url_colheita`, `url_minha_conta` e `modo_debug`.
- Mixins de perfil em `core/mixins.py`. As views da área logada ainda não usam mixins porque estão em mock; passam a usar na camada 1.
- Visual: Bootstrap 5.3.3 por CDN (com SRI) + `core/static/css/sustentagro.css` (paleta "Campo suave", tema claro/escuro por `data-bs-theme`). Componentes em `core/templates/componentes/`. Tela-exemplo: `ongs/templates/ongs/detalhe.html`.

## Deploy

- WSGI com Gunicorn (ADR-006): `Dockerfile` (python:3.13-slim, processo como `www-data`), `compose.yaml` com os serviços `app` e `postgres` (o script de backup do servidor espera esse nome) e as redes `web` e `db` (interna). A porta publicada vem de `APP_PORT` no `.env` e sempre começa com `127.0.0.1:`.
- O app recebe só as variáveis listadas em `environment` do compose (nunca o `POSTGRES_PASSWORD`). `docker/entrypoint.sh` roda `migrate` e `collectstatic` a cada início; `docker/postgres/init/01-app-db.sh` cria o banco e o usuário da aplicação na primeira inicialização.
- Estáticos em `staticfiles/` e uploads em `storage/uploads/` (`MEDIA_ROOT` pelo ambiente), montados do host e servidos pelo Nginx. `/saude/` responde `ok` (usado pelo healthcheck).
- O job `imagem` do CI sobe o compose completo e confere `/saude/`, `/` e o `collectstatic`.
- O roteiro de publicação e o site do Nginx com os valores reais ficam em `.claude/`, fora do Git.

## Testes

`core/tests/test_rotas.py` garante que as 15 telas abrem. Os testes de aceitação das regras (`*/tests/`) estão marcados com `@skip('Remova ao implementar o BL-xx')` e usam as fábricas de `core/tests/fabricas.py`, que importam os models dentro das funções. Ao implementar um item, remova o skip; não altere o teste para fazê-lo passar.

## Pontos de atenção

- O repositório é público: nunca escreva nele dados do servidor (nome, provedor, portas, caminhos, domínio, outros projetos). Use termos genéricos.
- `legado/` guarda o site estático da versão 1; o Django não lê essa pasta. A pasta `static/` da raiz, se existir localmente, é uma cópia antiga ignorada pelo Git.
- No Django 5, "Sair" precisa ser um POST (formulário no `base.html`).
- Estáticos e uploads em produção são servidos pelo Nginx (sem WhiteNoise); rode `collectstatic` antes de publicar.
- Arquivos de referência do projeto devem ser salvos e buscados na pasta `.claude/`.
