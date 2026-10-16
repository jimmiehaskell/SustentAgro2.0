# ADR-006 — Deploy manual em Docker na VPS e testes automáticos no GitHub Actions

## Status
Aceito (15/10/2026)

## Contexto
A VPS só expõe o Nginx do host. A aplicação roda em container com porta só em localhost, o banco fica em rede interna e nada é instalado no host (RNF-02, RNF-11). Estáticos e uploads são servidos pelo Nginx direto do disco (RNF-03). Só Jimmie acessa a VPS (D-30), e ele é o único revisor de PR (R-02). As regras implementadas com banco precisam de testes (RNF-09).

## Decisão
- **Imagem:** `Dockerfile` com Python, as dependências do `requirements.txt` e o Gunicorn. `compose.yaml` com os serviços `app` (porta uma porta local reservada) e `db` (PostgreSQL 18, rede interna, volume próprio), seguindo o roteiro "Como adicionar um novo projeto" da documentação da VPS.
- **Estáticos e uploads:** o `collectstatic` grava em `staticfiles/` e os uploads vão para `media/`, os dois montados do host. O Nginx serve `/static/` e `/media/` direto do disco, e o resto vai por `proxy_pass`. O WhiteNoise sai do projeto.
- **Configuração de produção:** `DEBUG=False`, segredos só no `.env` (RNF-04), `CSRF_TRUSTED_ORIGINS` e `SECURE_PROXY_SSL_HEADER` para HTTPS atrás do Nginx, e `TIME_ZONE = 'America/Sao_Paulo'`.
- **Publicação:** manual e feita só por Jimmie (`git pull`, `docker compose up -d --build --wait`, `migrate` e `collectstatic`), no fim de cada marco (project-plan.md §3).
- **CI:** o GitHub Actions roda, em cada pull request, `manage.py check`, `makemigrations --check` e os testes contra um PostgreSQL de serviço. O deploy não é automatizado.
- **Backup:** script padrão da VPS, em horário diferente do outro projeto do servidor (RNF-08).

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| WhiteNoise servindo os estáticos pela aplicação | Contraria RNF-03 e o padrão da VPS, em que o Nginx serve arquivos do disco |
| Deploy automático pelo GitHub Actions | Exigiria uma chave de acesso à VPS guardada no GitHub; a VPS é particular e profissional, e só Jimmie a manipula (D-30) |
| Sem CI, com os testes rodados à mão | Mais trabalho por revisão para o único revisor (decisão do usuário, 15/10/2026) |

## Consequências
- Um PR com teste quebrado fica vermelho antes da revisão, e Jimmie só revisa PR verde.
- O `makemigrations --check` no CI pega migration esquecida, erro comum de quem está começando no Django.
- O desenho Django nunca foi testado na VPS. A primeira publicação no M2, ainda com mock, existe para descobrir problemas cedo (R-03).
- Ao fim da matéria, remover o projeto da VPS significa apagar o diretório, o site do Nginx, o cron de backup e o certificado (D-30).

## Requisitos relacionados
RNF-02, RNF-03, RNF-04, RNF-08, RNF-09, RNF-11, D-22, D-30, R-02, R-03
