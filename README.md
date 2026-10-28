# SustentAgro 2.0

**Do campo à mesa, da vontade à ação.**

O SustentAgro conecta agricultores familiares, ONGs e cozinhas comunitárias e pessoas que querem ajudar.
O agricultor publica o excedente ou a produção fora do padrão estético; as ONGs próximas reservam e confirmam
o recebimento; e um painel público mostra o impacto da rede (kg salvos, famílias atendidas, renda gerada).
Quem quer ajudar encontra ONGs por causa (ODS), tipo de ajuda ou cidade e vê do que cada uma precisa agora.

Projeto acadêmico do Itinerário 5 – Trilha Cultura e Desenvolvimento Social, com foco nos ODS 2, 8 e 10.

## Documentos

| Documento | Para quê |
|---|---|
| [`docs/SustentAgro_2.0_Projeto.pdf`](docs/SustentAgro_2.0_Projeto.pdf) | Projeto completo e Guia do desenvolvedor |
| [`docs/prototipo.html`](docs/prototipo.html) | Protótipo navegável das 15 telas (abra no navegador) |
| [`docs/modelo-de-dados.pdf`](docs/modelo-de-dados.pdf) | Entidades, campos e relacionamentos |
| [`docs/requirements.md`](docs/requirements.md) | Requisitos, regras de negócio e glossário |
| [`docs/backlog.md`](docs/backlog.md) | Itens de trabalho, responsáveis e marcos |
| [`docs/architecture.md`](docs/architecture.md) e [`docs/adr/`](docs/adr/) | Arquitetura e decisões técnicas |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Como instalar, rodar e contribuir |

## Rodar localmente

```bash
python -m venv .venv && source .venv/Scripts/activate   # no Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Detalhes em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Tecnologia

Django 5.2 com páginas geradas no servidor, Bootstrap 5, PostgreSQL em produção e SQLite no desenvolvimento.

## Equipe

| Grupo | Integrantes |
|---|---|
| Desenvolvimento | Gabriel Ribeiro de Carvalho, Júlia Sernagiotto Barbosa, Pedro Freire de Farias, Vinicius Pereira Souza |
| Plataforma | Guilherme de Melo Lucas, João Matheus Bezerra, João Vitor de Freitas Silva, Vitor Gomes Araújo |
| Apresentação | Brayan Aragão Pletsch, Caio Vinício Nunes Vilarouca |
| Scrum master | Jimmie Haskell Gonçalves da Silva |

A versão 1 (site estático) está em [`legado/`](legado/).

Publicado em https://sustentagro.jimmiehaskell.dev 
