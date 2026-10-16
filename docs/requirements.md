# Requisitos — SustentAgro 2.0

> Documento vivo da Fase 1 (Concepção). Atualizado incrementalmente durante a entrevista.
>
> Fontes: `SustentAgro_2.0_Projeto.pdf` (PDF), o repositório (CÓDIGO), a documentação do servidor (VPS), a imagem do itinerário e a entrevista. Cada decisão da entrevista tem um ID `D-xx` no apêndice; os requisitos citam esses IDs.

## 0. Intake

| Pergunta | Resposta |
|---|---|
| Tipo de projeto | App web (Django 5.2, páginas renderizadas no servidor) |
| Greenfield ou existente | Existente: evolução do app Django atual, que hoje só tem carrossel de ONGs, seção "Sobre", login e admin |
| Porte | Trabalho acadêmico (Itinerário 5 – Trilha Cultura e Desenvolvimento Social): entrega e apresentação na faculdade; não precisa atender ONGs e agricultores reais agora |
| Protótipo navegável (Fase 4b) | Sim, além dos 7 wireframes estáticos do PDF |
| Diagrama de modelagem de dados (Fase 4a) | Sim |
| Entrega adicional pedida | Distribuição de tarefas para o grupo implementar |
| Hospedagem | servidor próprio (VPS), atrás do Nginx do host, em containers Docker |

### Ponto de partida observado no código

- Um único app (`ongs`) com o model `Ongs` (nome, nome curto, slogan, imagem, `about`, `is_active`). Sem cidade, ODS, tipo de ajuda ou CNPJ.
- ONGs cadastradas apenas pelo admin do Django; não há cadastro público nem perfis de usuário.
- Banco SQLite; `psycopg2-binary` e `gunicorn` já estão no `requirements.txt`, mas não configurados.
- Sem testes, sem Dockerfile, sem `compose.yaml`.

## 1. Problema

Alimentos bons para consumo são perdidos no campo (excedente ou fora do padrão estético) enquanto ONGs e cozinhas comunitárias têm demanda não atendida. Além disso, quem quer ajudar não consegue encontrar ONGs por causa, tipo de ajuda ou cidade, nem saber do que elas precisam agora.

Os dois problemas têm o mesmo peso.

## 2. Objetivos

- **OBJ-01** — Transformar o SustentAgro de vitrine de ONGs em rede ativa que conecta três públicos: doadores/voluntários, ONGs e agricultores familiares.
- **OBJ-02** — Levar o alimento que seria perdido no campo até quem tem fome, gerando renda para o pequeno produtor (ODS 2, 8 e 10).
- **OBJ-03** — Apresentar na VPS todas as telas (as 7 do PDF e as da área logada) navegáveis, com o fluxo da Colheita Solidária funcionando de verdade, com banco; as demais partes podem estar com dados fictícios fixos (mock) (D-28, revisa a versão de 13/10/2026).
- **OBJ-04** — Tornar o impacto visível e verificável (painel público), sustentando a fundamentação em Adorno e o critério de "ações com impacto social" do itinerário (D-11, D-13).

## 3. Stakeholders

| Nome/Papel | Interesse no projeto |
|---|---|
| Grupo do projeto (10 pessoas em três grupos, 4 programando, mais Jimmie como scrum master, D-29) | Planeja, implementa e apresenta a versão 2.0 |
| Avaliador(a) da faculdade (Itinerário 5) | Avalia a entrega: impacto social, articulação teoria–prática (Gramsci e Adorno), ODS prioritários |
| Dono da VPS (Jimmie Haskell) | Hospeda o projeto sem afetar o outro projeto do servidor já em produção |

Nenhuma ONG ou agricultor real participa nesta fase: são públicos-alvo, não stakeholders ativos. Os dados de demonstração são criados pelo grupo.

## 4. Escopo

As 7 telas do PDF mais a área logada de cada perfil (D-16):

| # | Entrega | Telas |
|---|---|---|
| E-01 | Busca e filtros de ONGs por ODS, tipo de ajuda e cidade | 01 Início, 02 Lista de ONGs |
| E-02 | Página da ONG com necessidades atuais e barras de progresso; ações de doar e voluntariar | 03 Página da ONG |
| E-03 | Cadastro e login por perfil (doador/voluntário, agricultor, ONG), com validação de CNPJ e aprovação de ONGs | 04 Cadastro por perfil |
| E-04 | Colheita Solidária: publicar oferta, listar, reservar parcialmente, confirmar recebimento | 05 Publicar excedente, 06 Ofertas para ONGs |
| E-05 | Painel de impacto público | 07 Painel de impacto |
| E-06 | Área logada "Minha conta" por perfil (ONG, agricultor, doador/voluntário) | Telas novas, não desenhadas no PDF |
| E-07 | Doação em dinheiro por promessa: o doador vê a chave Pix da ONG, registra o valor e a ONG confirma | Telas novas |
| E-08 | Dados de demonstração (ONGs, agricultores, ofertas e ações fictícias) | — |
| E-09 | Publicação na VPS em subdomínio próprio | — |

## 5. Fora do escopo

- Pagamento online: não há gateway; o dinheiro vai direto do doador à ONG, por Pix, fora do site (D-27).
- Geocodificação de endereço: a distância é calculada entre localidades, não entre endereços (D-27).
- Pagamento da venda "a preço justo" pelo site: é combinado e feito por fora (D-02).
- ONGs reais: as 9 atuais saem do site (D-17).
- ODS 3 e 18, e qualquer ODS além de 1, 2, 4, 5, 8 e 10 (D-14).
- Notificações por e-mail; o sistema não envia e-mail algum (D-21).
- Mensagens ou chat entre usuários (D-21).
- Logística de transporte: agendamento, rotas, motoristas (D-21).
- Recuperação de senha por e-mail (D-21).
- Login social, mapas e integração com redes sociais (D-25).
- Aplicativo móvel nativo (o site é responsivo, D-23).

## 6. Personas

| Persona | Necessidade principal |
|---|---|
| Visitante | Encontrar ONGs por causa, tipo de ajuda ou cidade e ver o impacto da rede, sem conta |
| Doador(a)/voluntário(a) | Saber do que uma ONG precisa agora, comprometer-se com algo concreto e acompanhar a contribuição |
| Agricultor(a) familiar | Dar destino ao excedente ou à produção fora do padrão, doando ou vendendo a preço justo; pode usar o celular (D-23) |
| ONG / cozinha comunitária | Publicar necessidades, receber doações e voluntários e reservar alimento do campo |
| Administrador(a) da plataforma | Aprovar ONGs e manter os cadastros; é alguém do grupo |

Uma conta de pessoa pode acumular os perfis de doador/voluntário e agricultor; conta de ONG é sempre só ONG (D-15).

## 7. Casos de uso

### UC-01 — Encontrar uma ONG
- **Ator**: visitante (ou qualquer usuário).
- **Pré-condição**: existir ao menos uma ONG ativa.
- **Fluxo principal**: na tela Início, busca por texto ou clica num ODS; na Lista, combina filtros de ODS, tipo de ajuda e cidade; abre a página da ONG.
- **Fluxo alternativo/erro**: nenhum resultado → mensagem "nenhuma ONG encontrada" e opção de limpar filtros.

### UC-02 — Cadastrar-se por perfil
- **Ator**: visitante.
- **Pré-condição**: nenhuma.
- **Fluxo principal**: escolhe o perfil na tela 04, preenche o formulário (ONG e agricultor escolhem a localidade numa lista) e o sistema cria a conta já logada.
- **Fluxo alternativo/erro**: perfil ONG → ver UC-03.

### UC-03 — Cadastrar e aprovar uma ONG
- **Ator**: representante da ONG; administrador.
- **Pré-condição**: CNPJ ainda não cadastrado.
- **Fluxo principal**: a ONG informa CNPJ e dados; o sistema valida dígitos e unicidade (e, se RF-35 for feito, consulta a API de CNPJ); a ONG fica "pendente"; o administrador aprova no admin do Django; a ONG passa a aparecer no site.
- **Fluxo alternativo/erro**: CNPJ inválido ou repetido → cadastro recusado. API fora do ar ou CNPJ não confirmado → cadastro segue pendente com o aviso "CNPJ não confirmado" e o administrador decide (D-18). Administrador reprova → a ONG não aparece e vê o motivo ao entrar.

### UC-04 — Publicar e gerir necessidades
- **Ator**: ONG aprovada.
- **Pré-condição**: estar logada.
- **Fluxo principal**: cria uma necessidade (título, tipo, unidade, meta), edita ou encerra; ela aparece na página da ONG com barra de progresso.
- **Fluxo alternativo/erro**: meta menor que o já confirmado → recusado.

### UC-05 — Prometer doação de itens
- **Ator**: doador.
- **Pré-condição**: estar logado; necessidade de itens aberta.
- **Fluxo principal**: clica em "Quero doar", escolhe a necessidade, informa a quantidade; a doação fica "prometida"; a ONG confirma o recebimento; a barra avança.
- **Fluxo alternativo/erro**: visitante sem login → é levado ao login/cadastro e volta à página. Doador cancela ou ONG recusa → a promessa é encerrada sem mover a barra.

### UC-06 — Inscrever-se como voluntário
- **Ator**: voluntário.
- **Pré-condição**: estar logado; necessidade de voluntários aberta.
- **Fluxo principal**: clica em "Quero ser voluntário(a)", escolhe a necessidade; fica "inscrito"; a ONG confirma; a barra avança.
- **Fluxo alternativo/erro**: os mesmos de UC-05.

### UC-07 — Doar dinheiro
- **Ator**: doador.
- **Pré-condição**: estar logado; ONG aceita dinheiro e informou a chave Pix.
- **Fluxo principal**: escolhe uma necessidade em reais ou doação livre, informa o valor e vê a chave Pix da ONG; a doação fica "prometida"; o doador faz o Pix por fora; a ONG confirma o recebimento; a doação conta e, se ligada a uma necessidade, a barra avança.
- **Fluxo alternativo/erro**: os mesmos de UC-05.

### UC-08 — Publicar oferta de colheita
- **Ator**: agricultor.
- **Pré-condição**: estar logado com perfil de agricultor.
- **Fluxo principal**: informa categoria, produto, quantidade e unidade, data "colher até", localidade (já preenchida com a do agricultor, alterável), estado, destino (doar ou vender, com preço), local de retirada, se precisa de transporte e, opcionalmente, uma ONG de destino; publica.
- **Fluxo alternativo/erro**: venda sem preço → recusado. Data "colher até" no passado → recusado.

### UC-09 — Reservar oferta de colheita
- **Ator**: ONG aprovada.
- **Pré-condição**: estar logada; oferta visível para ela e com saldo.
- **Fluxo principal**: filtra por distância, clica em "Reservar", informa a quantidade (até o saldo); o saldo da oferta diminui; ONG e agricultor passam a ver o contato um do outro.
- **Fluxo alternativo/erro**: duas ONGs reservam ao mesmo tempo mais que o saldo → a segunda é recusada com o saldo atualizado. ONG ou agricultor cancela antes do recebimento → a quantidade volta ao saldo.

### UC-10 — Confirmar recebimento da colheita
- **Ator**: ONG.
- **Pré-condição**: reserva ativa.
- **Fluxo principal**: marca a reserva como recebida; os kg (e a renda, se venda) entram no painel de impacto.
- **Fluxo alternativo/erro**: recebeu menos que o reservado → informa a quantidade recebida; só ela é contada.

### UC-11 — Acompanhar ofertas (agricultor)
- **Ator**: agricultor.
- **Pré-condição**: estar logado.
- **Fluxo principal**: vê as ofertas que publicou, o saldo, quem reservou e o contato; pode cancelar uma oferta ou uma reserva.

### UC-12 — Acompanhar contribuições (doador/voluntário)
- **Ator**: doador/voluntário.
- **Pré-condição**: estar logado.
- **Fluxo principal**: vê promessas, inscrições e doações em dinheiro com a situação de cada uma; pode cancelar as que ainda não foram confirmadas.

### UC-13 — Consultar o painel de impacto
- **Ator**: visitante.
- **Pré-condição**: nenhuma.
- **Fluxo principal**: abre "Impacto" e vê os quatro indicadores, o gráfico de kg por mês e a fatia de ações por ODS.
- **Fluxo alternativo/erro**: sem dados → indicadores zerados e mensagem no lugar do gráfico.

### UC-14 — Consultar ofertas sem ser ONG
- **Ator**: visitante ou doador.
- **Fluxo principal**: abre "Colheita Solidária" e vê a lista de ofertas abertas a todas, sem distância e sem botão de reserva, com convite para se cadastrar (D-26).

## 8. Requisitos funcionais

Camada (ver `project-plan.md` §1, D-28 e A-02): **1** = obrigatório com banco na apresentação; **2** e **3** = com banco se houver tempo, nessa ordem, senão em mock; **D** = desejável, só com folga. Toda tela existe em mock (camada 0), independentemente da camada do requisito.

| ID | Descrição | Critério de aceite | Camada | Origem |
|---|---|---|---|---|
| RF-01 | Busca de ONGs por texto na tela Início | Digitar parte do nome, do nome de um ODS ou da cidade lista só as ONGs ativas correspondentes | 1 | OBJ-01, PDF 3.1 |
| RF-02 | Cartões de ODS na tela Início | Os 6 ODS aparecem com a contagem real de ONGs ativas; clicar leva à Lista já filtrada | 1 | PDF tela 01, D-14 |
| RF-03 | Carrossel de ONGs na tela Início | Mostra ONGs ativas com imagem e leva à página da ONG | D | PDF tela 01 |
| RF-04 | Lista de ONGs com filtros | Filtros de ODS, tipo de ajuda e cidade combinam entre si (E lógico); o total exibido confere com os cartões | 1 | PDF 3.1 |
| RF-05 | Cartão da ONG na lista | Mostra foto, nome, resumo, selos de ODS e "Precisa agora" com a necessidade aberta mais recente | 1 | PDF tela 02 |
| RF-06 | Página da ONG | Mostra capa, nome, selos, descrição, necessidades abertas com "x de y unidade" e barra proporcional, e os botões de ação | 1 | PDF 3.2 |
| RF-07 | Cadastro por perfil | A tela 04 leva a três formulários; ao concluir, a conta existe com o perfil escolhido e a pessoa está logada | 1 | PDF 3.5 |
| RF-08 | Acúmulo de perfis | Uma conta de pessoa consegue ativar o segundo perfil (doador ↔ agricultor) em "Minha conta"; conta de ONG não tem essa opção | 3 | D-15 |
| RF-09 | Login e logout | Entrar com usuário e senha; o menu mostra "Minha conta" e "Sair" no lugar de "Cadastrar" | 1 | OBJ-03 |
| RF-10 | Validação de CNPJ | CNPJ com dígito verificador errado ou já cadastrado é recusado | 1 | D-07, D-27 |
| RF-11 | Aprovação de ONG | ONG nova nasce "pendente" e não aparece em telas públicas; após aprovação no admin, aparece; reprovada vê o motivo | 1 | D-07 |
| RF-12 | Perfil da ONG | A ONG edita descrição, imagens, ODS, tipos de ajuda aceitos, localidade, contato, chave Pix e famílias atendidas por mês | 1 | D-10, D-16, D-27 |
| RF-13 | Gestão de necessidades | A ONG cria, edita e encerra necessidades de tipo itens, dinheiro ou voluntariado, com unidade e meta | 2 | PDF 3.2, D-16 |
| RF-14 | Promessa de doação de itens | Doador logado registra quantidade para uma necessidade; fica "prometida" e não move a barra | 2 | D-05 |
| RF-15 | Inscrição de voluntário | Voluntário logado se inscreve numa necessidade de voluntários; fica "inscrito" e não move a barra | 2 | D-06 |
| RF-16 | Confirmação pela ONG | A ONG vê promessas (itens e dinheiro) e inscrições pendentes e confirma (com a quantidade ou o valor recebido) ou recusa; ao confirmar, a barra avança | 2 | D-05, D-06, D-27 |
| RF-17 | Doação em dinheiro | Doador logado registra um valor para uma necessidade em reais ou como doação livre e vê a chave Pix da ONG; a doação fica "prometida" até a ONG confirmar | 2 | D-24, D-27 |
| RF-18 | Publicar oferta de colheita | O formulário da tela 05, mais unidade, preço (se venda), localidade (preenchida com a do agricultor, alterável) e ONG de destino opcional, grava a oferta e ela aparece para quem pode vê-la | 1 | PDF 3.3, D-02, D-08 |
| RF-19 | Lista de ofertas para ONG | Mostra produto, saldo, local, distância em km entre a localidade da ONG e a da oferta, modalidade (com preço, se venda) e transporte; filtros "até 30 km", "até 60 km" e "todas" | 1 | PDF tela 06, D-27 |
| RF-20 | Reserva parcial | A ONG reserva de 1 até o saldo; o saldo diminui na hora; oferta com saldo zero sai da lista | 1 | D-09 |
| RF-21 | Oferta direcionada | Oferta com ONG de destino só aparece para essa ONG nas primeiras 48 h; depois aparece para todas | 3 | D-08 |
| RF-22 | Selo "urgente" | Oferta aberta a todas há mais de 48 h, com saldo, aparece com o selo e no topo da lista | 3 | D-08 |
| RF-23 | Confirmar recebimento da colheita | A ONG marca a reserva como recebida informando a quantidade; a reserva passa a contar no painel | 1 | D-09 |
| RF-24 | Cancelar reserva ou oferta | ONG ou agricultor cancela uma reserva não recebida e a quantidade volta ao saldo; agricultor cancela uma oferta sem reservas ativas | 3 | UC-09, UC-11 |
| RF-25 | Minhas ofertas (agricultor) | O agricultor vê ofertas, saldo, reservas, situação e contato da ONG | 1 | D-16 |
| RF-26 | Minhas contribuições (doador) | O doador vê promessas, inscrições e doações em dinheiro com a situação, e cancela as não confirmadas | 2 | D-16 |
| RF-27 | Contato após reserva | Só depois da reserva a ONG vê telefone/e-mail do agricultor e vice-versa | 1 | D-21 |
| RF-28 | Ofertas para visitante | Visitante e doador veem as ofertas abertas a todas, sem distância, contato ou botão de reserva | 1 | D-26 |
| RF-29 | Painel: indicadores | Mostra kg salvos, famílias atendidas, renda gerada e ONGs ativas, calculados conforme RN-08 a RN-11 | 1 | PDF 3.4 |
| RF-30 | Painel: kg por mês | Gráfico de barras com os kg recebidos por mês | 1 | PDF tela 07 |
| RF-31 | Painel: fatia por ODS | Uma barra por ODS com a porcentagem das ações confirmadas, conforme RN-07; com só a camada 1 pronta, as ações são as reservas de colheita recebidas (E-10) | 1 | D-13 |
| RF-32 | Carga de dados de demonstração | Um comando recria localidades, ONGs, agricultores, doadores, necessidades, ofertas e ações fictícias, suficiente para todas as telas terem conteúdo; na camada 1 é a única fonte de necessidades (A-01) | 1 | E-08, D-13 |
| RF-33 | Localidade no cadastro | ONG e agricultor escolhem a localidade numa lista que já traz latitude e longitude; o endereço de retirada é texto livre, só informativo. A lista vem da carga de dados (RF-32) e o administrador a edita pelo admin do Django | 1 | D-27, P-06, A-05 |
| RF-34 | Seção "Sobre" atualizada | Mantém a seção sobre o projeto com a lista da equipe do PDF | D | CÓDIGO |
| RF-35 | Consulta externa de CNPJ | No cadastro da ONG, o sistema consulta uma API pública de CNPJ e mostra ao administrador se o número existe e está ativo; se a API falhar, o cadastro segue pendente com "CNPJ não confirmado" | D | D-07, D-18, D-27 |

## 9. Requisitos não funcionais

Reduzidos aos críticos, por se tratar de trabalho acadêmico.

| ID | Categoria | Descrição |
|---|---|---|
| RNF-01 | Usabilidade | Todas as telas, públicas e logadas, funcionam em celular (largura de 360 px) e em computador (D-23) |
| RNF-02 | Implantação | Roda em containers na servidor próprio (VPS): aplicação com porta publicada só em localhost, banco PostgreSQL em rede Docker interna, nada instalado no host |
| RNF-03 | Implantação | Arquivos estáticos e imagens enviadas são servidos pelo Nginx do host direto do disco, não pela aplicação |
| RNF-04 | Segurança | Segredos (chave do Django e senhas do banco) só no `.env`, fora do Git; `DEBUG` desligado em produção |
| RNF-05 | Segurança | Cada perfil só altera os próprios dados: uma ONG não edita necessidades de outra, um agricultor não cancela oferta de outro |
| RNF-06 | Segurança | Upload de imagem limitado a jpeg, jpg, png e webp, até 10 MB (limite do Nginx da VPS) |
| RNF-07 | Disponibilidade | Se RF-35 for feito, falha da API de CNPJ não impede o cadastro nem derruba a página |
| RNF-08 | Manutenção | Backup diário do banco e dos uploads pelo script padrão da VPS |
| RNF-09 | Qualidade | Regras de negócio implementadas com banco cobertas por testes automatizados (as que ficarem em mock não têm teste) |
| RNF-10 | Idioma | Interface inteira em português do Brasil |
| RNF-11 | Isolamento | A implantação não altera containers, banco, site ou certificado do outro projeto do servidor |

## 10. Regras de negócio

| ID | Regra | Origem |
|---|---|---|
| RN-01 | Só ONG aprovada e não desativada ("ativa") aparece em telas públicas, cria necessidades e reserva ofertas | D-07 |
| RN-02 | A barra de uma necessidade só avança com quantidade ou valor confirmado pela ONG; promessa e inscrição pendentes não contam | D-05, D-06, D-27 |
| RN-03 | A soma das reservas ativas e recebidas de uma oferta nunca passa da quantidade publicada | D-09 |
| RN-04 | Oferta com ONG de destino fica visível só para ela durante 48 h a partir da publicação; depois, para todas as ONGs ativas | D-08 |
| RN-05 | Oferta sem ONG de destino fica visível para todas as ONGs ativas desde a publicação | D-08 |
| RN-06 | Oferta com saldo, aberta a todas há mais de 48 h, é "urgente" | D-08 |
| RN-07 | Ação confirmada = doação de item confirmada, voluntariado confirmado, doação em dinheiro confirmada ou reserva de colheita recebida. Cada ação conta uma vez para cada ODS da ONG que a recebeu; a porcentagem de um ODS é a sua contagem dividida pela soma das contagens | D-13 |
| RN-08 | Kg salvos = soma das quantidades recebidas, em kg, das reservas de colheita | D-09 |
| RN-09 | Renda gerada = soma de preço × quantidade recebida das reservas de ofertas de venda | D-02 |
| RN-10 | Famílias atendidas = soma do valor declarado no perfil de cada ONG ativa | D-10 |
| RN-11 | ONGs ativas = contagem das ONGs que satisfazem RN-01 | D-07 |
| RN-12 | Uma pessoa pode ter os perfis de doador/voluntário e agricultor na mesma conta; conta de ONG tem só o perfil ONG | D-15 |
| RN-13 | Oferta de venda exige preço; oferta de doação não tem preço | D-02 |
| RN-14 | Só o administrador da plataforma aprova, reprova ou desativa ONGs | D-07 |
| RN-15 | A distância entre uma ONG e uma oferta é a distância em linha reta entre as coordenadas da localidade da ONG e da localidade da oferta; mesma localidade = 0 km | D-27, A-03 |
| RN-16 | Quantidades em kg aceitam uma casa decimal; em unidades, só inteiros (ofertas, reservas e recebimentos) | E-01 |
| RN-17 | A quantidade recebida vai de 0 até a quantidade reservada; recebido 0 encerra a reserva sem contar no painel e devolve a quantidade ao saldo, se a oferta não venceu | E-02, E-03 |
| RN-18 | Quando a oferta vence, as reservas não recebidas continuam válidas até a ONG confirmar ou cancelar; só o saldo não reservado sai da lista | E-04 |
| RN-19 | Ao desativar uma ONG, as reservas ativas dela são canceladas e as quantidades voltam ao saldo das ofertas | E-05 |
| RN-20 | ONG pendente ou reprovada só acessa a "Minha conta": vê a situação do cadastro (e o motivo, se reprovada) e edita o perfil | E-06 |
| RN-21 | Necessidade que atinge a meta fica "atendida" (barra em 100%) e não aceita novas promessas nem inscrições; a ONG reabre aumentando a meta | E-07 |
| RN-22 | Visitante e doador veem só o nome da localidade da oferta; o texto do local de retirada aparece para ONGs, e o contato só para a ONG que reservou | E-08 |
| RN-23 | O gráfico de kg por mês agrupa pela data do recebimento | E-09 |
| RN-24 | Os CNPJs das ONGs fictícias da carga de dados têm dígitos verificadores válidos e são únicos | E-11 |
| RN-25 | Conta com perfis de doador e agricultor que clica em "Colheita Solidária" cai em publicar oferta, com link para a lista de ofertas | E-12 |

## 11. Integrações

Nenhuma integração obrigatória (D-27). O sistema funciona sem serviço externo.

| Integração | Uso | Prioridade | Se estiver fora do ar |
|---|---|---|---|
| Consulta de CNPJ | Informar ao administrador se o CNPJ existe e está ativo (RF-35) | Desejável: só se sobrar tempo | Cadastro segue pendente com "CNPJ não confirmado" (D-18) |

Removidas do escopo: gateway de pagamento e geocodificação de endereço.

## 12. Restrições

- **Prazo**: até cerca de 10/11/2026, 4 semanas a partir de 13/10/2026 (D-19).
- **Equipe**: 4 pessoas programando (grupo Desenvolvimento), dividindo backend e frontend, com Jimmie como scrum master e apoio (D-29, `project-plan.md` §0).
- **Tecnologia**: evolução do app Django 5.2 existente.
- **Hospedagem**: servidor próprio (VPS). Só o Nginx do host fica exposto; aplicação em container com porta apenas em localhost; banco em container próprio em rede interna; nenhuma linguagem no host. Para Django, a documentação prevê Gunicorn atrás de `proxy_pass` e estáticos do `collectstatic` servidos pelo Nginx, desenho que ainda não foi testado nessa VPS.
- **Domínio**: subdomínio de domínio do scrum master, com DNS no provedor de DNS em modo "Somente DNS" e certificado novo (D-22).
- **Orçamento**: sem custos; a única integração possível (RF-35) precisa ser gratuita.

## 13. Critérios de aceite gerais

- As 7 telas do PDF e a área logada estão acessíveis em HTTPS no subdomínio da VPS e são navegáveis; as que ainda não têm backend mostram dados fictícios fixos (mock) (D-28).
- **Obrigatório com banco:** o fluxo da Colheita pode ser demonstrado do início ao fim, sem tocar no banco à mão: cadastro/login → agricultor publica uma oferta → ONG reserva parte → ONG confirma o recebimento → kg (e renda, se venda) aparecem no painel.
- **Se houver tempo, também com banco** (na ordem das camadas do `project-plan.md`):
  - ONG cria uma necessidade → doador promete itens → ONG confirma → a barra avança.
  - Doador registra uma doação em dinheiro e vê a chave Pix da ONG → a ONG confirma → a barra da necessidade avança.
- O cadastro de uma ONG nova fica pendente e só aparece no site depois de aprovado.
- Todas as telas são utilizáveis em um celular.
- Os testes automatizados cobrem as regras de negócio já implementadas com banco.
- O outro projeto do servidor continua respondendo normalmente após a publicação.

## 14. Glossário

| Termo | Definição |
|---|---|
| ODS | Objetivo de Desenvolvimento Sustentável. O catálogo do sistema tem seis: 1, 2, 4, 5, 8 e 10 |
| ONG ativa | ONG aprovada pelo administrador e não desativada |
| ONG pendente | ONG cadastrada que ainda não foi aprovada; invisível nas telas públicas |
| Necessidade | Pedido de uma ONG com tipo (itens, dinheiro ou voluntariado, os mesmos valores do tipo de ajuda), unidade e meta |
| Tipo de ajuda | Itens, dinheiro ou voluntariado |
| Promessa | Doação de itens ou de dinheiro registrada pelo doador e ainda não confirmada pela ONG |
| Inscrição | Candidatura de um voluntário a uma necessidade, ainda não confirmada pela ONG |
| Oferta | Excedente ou produção fora do padrão publicada por um agricultor |
| Oferta direcionada | Oferta com uma ONG de destino escolhida pelo agricultor |
| Saldo | Quantidade da oferta ainda não reservada |
| Reserva | Parte de uma oferta que uma ONG se comprometeu a receber |
| Recebimento | Confirmação, pela ONG, de que a reserva chegou; é o que conta no painel |
| Preço justo | Preço informado pelo agricultor na oferta de venda; o pagamento ocorre fora do site |
| Ação confirmada | Ver RN-07 |
| Localidade | Cidade ou região de uma lista mantida pelo sistema, com latitude e longitude; base do filtro por cidade e do cálculo de distância. ONG, agricultor e cada oferta têm a sua |
| Dados de demonstração | ONGs, pessoas, ofertas e ações fictícias criadas pelo grupo |

## 15. Decisões menores aprovadas no gate (13/10/2026)

Pontos menores que a entrevista não cobriu. Todos foram aprovados pelo usuário no gate da Fase 1 e valem como decisão.

| ID | Ponto | Decisão |
|---|---|---|
| P-01 | Unidade da oferta | Quilos ou unidades (o wireframe mostra "un." para alface). Só ofertas em kg entram em "kg salvos" |
| P-02 | Preço da oferta de venda | Informado por kg ou por unidade, conforme a unidade da oferta |
| P-03 | Vencimento da oferta | Depois da data "colher até", o saldo não reservado sai da lista como "expirado" |
| P-04 | Tipos de ajuda da ONG | A ONG marca no perfil quais aceita; os filtros da lista usam essa marcação |
| P-05 | Selo "urgente" em oferta direcionada | As 48 h do selo contam a partir do momento em que a oferta abre para todas |
| P-06 | Conteúdo da lista de localidades | Lista própria, mantida pelo administrador e carregada com as regiões administrativas do DF e os municípios do Entorno. Motivo: com a lista de municípios do IBGE, tudo no DF seria "Brasília" e toda distância daria 0 km |
| P-07 | Promessa nunca confirmada | Fica "prometida" até a ONG confirmar ou recusar, ou o doador cancelar; não vence sozinha |
| P-08 | Nome do subdomínio | subdomínio próprio do projeto |
| P-09 | Lista da equipe na seção "Sobre" | Os 11 nomes da lista oficial do grupo (16/10/2026): Brayan Aragão Pletsch, Caio Vinício Nunes Vilarouca, Gabriel Ribeiro de Carvalho, Guilherme de Melo Lucas, Jimmie Haskell Gonçalves da Silva, João Matheus Bezerra, João Vitor de Freitas Silva, Júlia Sernagiotto Barbosa, Pedro Freire de Farias, Vinicius Pereira Souza e Vitor Gomes Araújo. Sai Vitor Hugo Alves da Silva, que está no site atual. O RGM não aparece no site |
| P-10 | Data exata da apresentação | Planejar para 10/11/2026 até você informar a data real |
| P-11 | Administrador | Usa só o admin do Django, sem tela própria no site |

## Apêndice — Decisões da entrevista (registro cronológico)

| # | Lacuna | Decisão | Origem |
|---|---|---|---|
| D-01 | 1 — Localização e distância | A pessoa informa endereço/CEP e um serviço externo de geocodificação devolve as coordenadas; a distância em km é calculada a partir delas. Gera uma integração externa (seção 11). A escolha do serviço fica para a Fase 4. | [ENTREVISTA] |
| D-02 | 2 — Preço justo e pagamento | O agricultor informa o preço ao publicar a oferta; a ONG vê e reserva; o pagamento é combinado e feito fora do site. O valor informado alimenta a 'renda gerada' do painel de impacto. Sem gateway de pagamento. | [ENTREVISTA] |
| D-03 | 3 — 'Quero doar' e doação em dinheiro | Doação em dinheiro com pagamento online pelo site, via gateway. Gera uma integração externa (seção 11). Detalhes (dinheiro real ou ambiente de teste, quem recebe) em D-04. | [ENTREVISTA] |
| D-04 | 3 — Pagamento: real ou teste | Integração real com o gateway, porém com credenciais de teste (sandbox): o fluxo completo funciona na apresentação e nenhum dinheiro circula. Dinheiro real fica fora do escopo. A escolha do gateway fica para a Fase 4. | [ENTREVISTA] |
| D-05 | 3 e 7 — Doação de itens e barra de progresso | O doador logado escolhe uma necessidade da ONG e informa a quantidade; a doação fica como 'prometida'. A barra de progresso só avança quando a ONG confirma o recebimento. | [ENTREVISTA] |
| D-06 | Voluntariado | Mesmo fluxo de D-05: o voluntário logado se inscreve numa necessidade de voluntários; fica 'inscrito' e a barra só avança quando a ONG confirma. | [ENTREVISTA] |
| D-07 | 4 — Validação por CNPJ | O sistema valida os dígitos verificadores e a unicidade, consulta uma API pública de CNPJ para confirmar existência e situação ativa, e a ONG fica 'pendente' até um administrador aprovar; só então aparece no site. Gera uma integração externa (seção 11) e um papel de administrador da plataforma. | [ENTREVISTA] |
| D-08 | 5 — Regra das 48 h | Ao publicar, o agricultor pode opcionalmente direcionar a oferta a uma ONG. Se direcionar, só essa ONG vê a oferta por 48 h; sem reserva nesse prazo, ela abre para todas. Se não direcionar, todas as ONGs veem desde o início. Oferta aberta a todas há mais de 48 h sem reserva ganha o selo 'urgente' e sobe na lista. (Para oferta direcionada, o ponto de partida dessas 48 h do selo — publicação ou abertura a todas — está a confirmar.) **Superado em parte por P-05.** | [ENTREVISTA] |
| D-09 | Reserva de oferta | Reserva parcial: a ONG reserva parte da quantidade e o restante continua disponível para outras ONGs. O recebimento é confirmado pela ONG; só então os kg (e a renda, se venda) entram no painel de impacto. | [ENTREVISTA] |
| D-10 | 6 — Famílias atendidas | Cada ONG declara no próprio perfil quantas famílias atende por mês; o painel soma os valores das ONGs ativas. O número não varia com as doações. | [ENTREVISTA] |
| D-11 | Expectativa do avaliador (imagem 'WhatsApp Image 2026-09-29 at 18.12.50.jpeg') | Itinerário 5 — objetivo: formar estudantes com consciência crítica, social e cultural, articulando teoria e prática em ações com impacto social e cultural. Competências: responsabilidade social, empatia, pensamento crítico, comunicação eficaz e autonomia. Destaques: projetos baseados em Gramsci e Adorno, com diagnóstico e intervenção em territórios diversos. ODS prioritários do itinerário: 1, 2, 3, 4, 5, 8, 10 e 18 (o PDF usa 1, 2, 4, 5, 8 e 10; os ODS 3 e 18 não aparecem no PDF — a confirmar se entram no catálogo). **Resolvido por D-14.** | [ENTREVISTA] |
| D-12 | Nomes dos ODS no painel | ODS 1 – Erradicação da pobreza; ODS 2 – Fome zero e agricultura sustentável; ODS 8 – Trabalho decente e crescimento econômico; ODS 10 – Redução das desigualdades. | [ENTREVISTA] |
| D-13 | Percentual do bloco 'Impacto por ODS' | Fatia das ações confirmadas: cada ação confirmada pela ONG (doação de item, voluntariado, doação em dinheiro, reserva de colheita recebida) conta para os ODS dessa ONG; a barra de cada ODS mostra sua fatia no total de ações. Uma ONG com dois ODS conta nos dois. O grupo prepara dados de demonstração para a apresentação. | [ENTREVISTA] |
| D-14 | Catálogo de ODS | Os 6 do PDF: 1, 2, 4, 5, 8 e 10. Os ODS 3 e 18 do itinerário ficam fora do catálogo nesta versão. Resolve a pendência anotada em D-11. | [ENTREVISTA] |
| D-15 | 8 — Acúmulo de perfis | Uma conta de pessoa pode ser doador/voluntário e agricultor ao mesmo tempo. Conta de ONG é sempre só ONG, por representar uma organização. | [ENTREVISTA] |
| D-16 | Telas de gestão não desenhadas no PDF | Cada perfil ganha uma área logada própria ('Minha conta') no site, com o mesmo visual das 7 telas: ONG (necessidades, confirmação de doações/voluntários, reservas e recebimento, edição de perfil), agricultor (ofertas publicadas, reservas, cancelamento), doador/voluntário (promessas e inscrições), pagamento (doação em dinheiro e retorno do gateway; **o gateway foi removido por D-27**). Só o administrador da plataforma usa o admin do Django (aprovação de ONGs). | [ENTREVISTA] |
| D-17 | ONGs atuais do site | As 9 ONGs reais saem; a versão 2.0 usa apenas ONGs fictícias, para não atribuir a organizações reais necessidades e números que elas não informaram. Afeta o carrossel da tela 01 e os exemplos dos wireframes (nomes de ONGs reais). | [ENTREVISTA] |
| D-18 | Conflito D-07 x D-17 (CNPJ fictício) | Se a consulta à API de CNPJ falhar ou não confirmar o número, o cadastro fica pendente com o aviso 'CNPJ não confirmado' e o administrador decide. As ONGs fictícias passam pelo cadastro normal e são aprovadas manualmente. Cobre também o caso de a API estar fora do ar. Ajusta D-07: a consulta externa informa a decisão do administrador, não bloqueia o cadastro. | [ENTREVISTA] |
| D-19 | Prazo | Entrega em até 4 semanas a partir de 13/10/2026, ou seja, até cerca de 10/11/2026. Data exata da apresentação a confirmar. **Resolvido por P-10.** | [ENTREVISTA] |
| D-20 | Equipe | 7 das 10 pessoas da equipe vão programar nesta versão. Nomes e nível de experiência de cada uma serão levantados na Fase 2, para a distribuição de tarefas. **Adiado para até 17/10, com distribuição no backlog da Fase 4 (`project-plan.md` §8).** **Superada por D-29.** | [ENTREVISTA] |
| D-21 | Fora do escopo | Ficam fora desta versão: notificações por e-mail (novidades só aparecem na área logada); mensagens/chat entre usuários (o site mostra o contato da outra parte após a reserva); logística de transporte (a oferta só indica 'precisa de transporte' ou 'agricultor leva'); recuperação de senha por e-mail (só o administrador redefine senhas). Já estavam fora: dinheiro real, pagamento da venda pelo site, ONGs reais, ODS 3 e 18. Consequência: o sistema não precisa de serviço de envio de e-mail. | [ENTREVISTA] |
| D-22 | 9 — Domínio na VPS | Subdomínio do domínio do scrum master (nome exato a confirmar; sugestão: subdomínio próprio do projeto; **resolvido por P-08**). Exige registro DNS no provedor de DNS em modo 'Somente DNS' e certificado novo, conforme o roteiro 'Como adicionar um novo projeto' da documentação da VPS. | [ENTREVISTA] |
| D-23 | Uso em celular | Todas as telas (públicas e da área logada) devem se adaptar ao celular. | [ENTREVISTA] |
| D-24 | Doação em dinheiro: vínculo | As duas formas: o doador paga para uma necessidade com meta em reais (a barra avança quando o gateway confirma o pagamento) ou faz uma doação livre à ONG, que fica no histórico e conta como ação no painel sem mover barra. | [ENTREVISTA] |
| D-25 | Integrações | Somente três: geocodificação de endereço/CEP, consulta de CNPJ e gateway de pagamento em modo de teste. Login com usuário e senha do próprio site; sem login social, sem mapa, sem redes sociais. | [ENTREVISTA] |
| D-26 | Menu 'Colheita Solidária' | Depende do perfil: agricultor cai em publicar oferta; ONG cai na lista de ofertas com o botão Reservar; visitante e doador veem a lista de ofertas só para consulta, sem distância nem botão, com convite para se cadastrar. | [ENTREVISTA] |
| D-27 | Redução de risco de prazo (revisa D-01, D-03, D-04, D-07, D-24 e D-25) | Sai o gateway de pagamento: a doação em dinheiro vira promessa, com a chave Pix da ONG exibida ao doador e confirmação pela ONG. Sai a geocodificação: ONG e agricultor escolhem a localidade numa lista com coordenadas, e a distância é calculada entre localidades. A consulta externa de CNPJ passa a desejável (RF-35); o obrigatório é dígitos verificadores, unicidade e aprovação do administrador. | [ENTREVISTA] |
| D-28 | Estratégia de entrega (14/10/2026, Fase 2; revisa OBJ-03, critérios de aceite gerais e RNF-09) | Primeiro todas as telas ficam prontas e navegáveis com dados fictícios fixos (mock); depois o backend substitui os mocks na ordem das camadas. Não é preciso estar 100% funcional na apresentação. Mínimo obrigatório com banco: o fluxo da Colheita Solidária (cadastro/login, publicar, reservar, confirmar recebimento, painel). | [ENTREVISTA] |
| D-29 | Equipe e papéis (15/10/2026, revisa D-20) | Três grupos mais o scrum master. Apresentação (Caio, Brayan): presença, apresentação e relatório com o avaliador. Plataforma (João Matheus, Guilherme Lucas, João Vitor, Vitor Gomes): preenchimento do DreamShaper. Desenvolvimento (Vinicius, Julia, Gabriel Ribeiro, Pedro Freire): todo o código, backend e frontend. Jimmie é o scrum master, auxilia os três grupos e não concentra mais o backend. Programam 4 pessoas, não 7. | [ENTREVISTA] |
| D-30 | Grupo Plataforma e VPS (15/10/2026) | A avaliação se apoia principalmente no preenchimento do DreamShaper, com fotos e vídeos do sistema. Para isso, gera-se um novo `SustentAgro_2.0_Projeto.pdf`, detalhado, com o que o sistema terá e fará e como vai funcionar. A VPS é manipulada só por Jimmie, e o projeto fica nela só até a aprovação na matéria. O grupo Desenvolvimento usou Python e HTML/CSS; Django, presumivelmente não. | [ENTREVISTA] |
| D-31 | Guia do desenvolvedor no PDF (15/10/2026) | O novo `SustentAgro_2.0_Projeto.pdf` inclui, além da parte para a Plataforma, um passo a passo para cada dev navegar pelos documentos gerados e saber onde consultar cada arquivo, requisito e regra de negócio ao implementar um item do backlog. | [ENTREVISTA] |
| D-32 | Paleta "Campo suave" (16/10/2026, Fase 4b) | Paleta do site ajustada a partir da versão 1 para cansar menos a vista: verde de campo `#3D7A16` (era `#3D830E`), limão suave `#A6E36B` (era `#7EFF2A`), carvão `#1D1F1C` (era `#1D1D1D`) e verde claro de apoio `#EAF7DC`. Menu e áreas grandes neutros; cor cheia só no que se clica. Tema escuro com fundo `#1A1D19` e texto `#E6EAE2`. O site segue o tema do sistema e tem botão para alternar. Tipografia: Bricolage Grotesque (títulos) e Figtree (texto), pelo Google Fonts. | [ENTREVISTA] |

---
**Status da fase**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 13/10/2026 (revisado em 14/10/2026 por D-28, na Fase 2, e pelo `analysis-report.md`, na Fase 3)
