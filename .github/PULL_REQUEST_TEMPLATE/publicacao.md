## Publicação main → prod

<!-- Título: "Publicação: <resumo>". Ao mesclar, use "Create a merge commit" (Merge), nunca "Squash and merge". -->

| PR | O que muda | Afeta o site? |
|---|---|---|
| #<!-- número --> | <!-- uma frase --> | <!-- Sim / Não --> |

<!-- Para listar o que vai ser publicado: git fetch; git log --oneline --no-merges origin/prod..origin/main -->

## Antes do merge

- [ ] CI verde (`testes` e `imagem`)
- [ ] Migrations novas? Se sim, são compatíveis com a versão anterior do código (a volta automática não desfaz migrations)
- [ ] Mudou `compose.yaml` ou `docker/postgres/`? Se sim, aplicar à mão no servidor (o deploy não aplica esses arquivos)
- [ ] Variável nova de ambiente? Se sim, já está no `.env` do servidor

## Depois do merge

- [ ] Avisos de publicação "iniciando" e "concluído" recebidos
- [ ] `/saude/` responde `ok`
- [ ] As telas alteradas abrem no site
