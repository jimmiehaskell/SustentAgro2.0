# Como contribuir com o SustentAgro 2.0

Guia prático para o grupo Desenvolvimento. Para entender **o que** construir, leia antes a Parte 2 do
`docs/SustentAgro_2.0_Projeto.pdf` (Guia do desenvolvedor). Este arquivo explica **como** trabalhar no código.

## 1. Preparar o computador (uma vez)

Você precisa de Python 3.13 ou mais novo, Git e um editor (PyCharm ou VS Code).

```bash
git clone https://github.com/jimmiehaskell/SustentAgro2.0.git
cd SustentAgro2.0
python -m venv .venv
source .venv/Scripts/activate      # Git Bash no Windows; no PowerShell: .venv\Scripts\Activate.ps1
source .venv/bin/activate          # no Mac/Linux (no lugar da linha acima)
pip install -r requirements.txt
cp .env.example .env               # depois troque a SECRET_KEY por qualquer texto longo
python manage.py migrate
python manage.py runserver
```

Abra http://127.0.0.1:8000. O banco local é um arquivo SQLite (`db.sqlite3`); não é preciso instalar banco.

## 2. Navegar pelas telas com perfis diferentes

Enquanto as telas estão com dados de exemplo (mock), uma barra escura no topo do site (só com `DEBUG=True`)
troca o perfil simulado: visitante, pessoa, agricultor, ong, ong-pendente e ong-reprovada.
O menu e as telas mudam conforme o perfil, como no protótipo (`docs/prototipo.html`).

## 3. Pegar um item e trabalhar

1. No quadro do projeto no GitHub, pegue uma issue sua da coluna "A fazer" e mova para "Em andamento".
2. Atualize o `main` e crie um branch com o código do item:
   ```bash
   git switch main
   git pull
   git switch -c bl-15-lista-ongs
   ```
3. Siga o passo a passo da issue (ela aponta para os requisitos, os casos extremos, a tela e os testes).
4. Rode os testes antes de enviar:
   ```bash
   python manage.py test
   ```
5. Faça commits pequenos, em português:
   ```bash
   git add .
   git commit -m "BL-15: filtros combinados na lista de ONGs"
   git push -u origin bl-15-lista-ongs
   ```
6. Abra o pull request no GitHub. O título começa com o código do item ("BL-15 · Lista de ONGs") e a
   descrição tem `Fecha #número-da-issue`. Preencha o checklist.
7. Espere o CI ficar verde e a revisão do Jimmie. Se ele pedir mudança, faça no mesmo branch e dê `git push` de novo.

## 4. Onde cada coisa fica

| O quê | Onde |
|---|---|
| Configurações | `core/settings.py` (lê o `.env`) |
| Base visual, menu e componentes | `core/templates/base.html`, `core/templates/componentes/`, `core/static/css/sustentagro.css` |
| Tela-exemplo (copie o padrão) | `ongs/templates/ongs/detalhe.html` |
| Apps | `contas`, `ongs`, `colheita`, `doacoes`, `painel` (um por área, ADR-001) |
| Dados de exemplo | `<app>/mocks.py` (mesmos nomes de campo do modelo de dados) |
| Regras de negócio | `<app>/services.py` (nunca na view) |
| Listas de valores | `<app>/choices.py` |
| Models a criar | comentários em `<app>/models.py`, campo a campo |
| Testes | `<app>/tests/` |
| Proteção por perfil | `core/mixins.py` |
| Documentos do projeto | `docs/` |

## 5. Regras do grupo

- Textos da interface, comentários e commits em português do Brasil.
- Use os nomes de campo do modelo de dados, tanto no mock quanto no model.
- Regra de negócio fica no `services.py`; a view só chama o serviço e escolhe o template.
- Estilo novo vai para `sustentagro.css`; nada de CSS solto no template. Use as classes do Bootstrap 5.
- Toda tela precisa funcionar com 360 px de largura e nos temas claro e escuro.
- Toda view da área logada usa um mixin de `core/mixins.py` (a partir da camada 1).
- Ao implementar um item, remova o `@skip` dos testes dele. Teste vermelho é sinal de que a regra ainda não
  está certa; não apague o teste.
- Nunca envie direto para o `main`, nem o `.env`, nem o `db.sqlite3`.

## 6. Como o código chega ao site

- Todo PR de vocês vai para o **`main`**. Nunca abram PR para a branch `prod`.
- A `prod` é o que está no ar. Só o Jimmie publica, com um PR `main → prod` usando **Merge** (não *squash*).
  Cada merge na `prod` é publicado automaticamente no servidor em 1 ou 2 minutos.
- O servidor faz backup antes de publicar e volta sozinho para a versão anterior se a nova não responder.
  Mas ele **não desfaz migrations**: por isso, uma migration precisa ser compatível com a versão anterior do código.
  Na prática: para tornar um campo obrigatório, primeiro crie o campo com valor padrão (ou aceitando vazio),
  publique, e só depois torne obrigatório. Na dúvida, pergunte ao Jimmie no PR.

## 7. Trocar uma tela de mock para banco

1. Crie os models do item (os campos estão comentados no `models.py` do app).
2. `python manage.py makemigrations <app>` e `python manage.py migrate`.
3. Na view, troque o `mocks.ALGUMA_COISA` pela consulta ao banco e apague o comentário `# MOCK`.
4. O template não deve mudar: se mudar, algum nome de campo está diferente do modelo de dados.
5. Proteja a view com o mixin certo.

## 8. Dúvidas

Antes de inventar uma regra, procure o código dela (RF-xx, RN-xx) com `Ctrl+Shift+F` no editor, dentro de
`docs/`. Se não achar, pergunte ao Jimmie na própria issue.
