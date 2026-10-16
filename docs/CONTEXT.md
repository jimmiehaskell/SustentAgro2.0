# Contexto do Sistema — SustentAgro 2.0

> Documento da Fase 4 (Design). Primeiro artefato desta fase: situa o sistema antes das decisões de arquitetura. Parte de `requirements.md`, `project-plan.md` e `analysis-report.md` aprovados (último em 15/10/2026).

## 1. Resumo

O SustentAgro é um site que conecta três públicos: pessoas que querem doar ou ser voluntárias, ONGs e cozinhas comunitárias, e agricultores familiares. Quem visita encontra ONGs por causa (ODS), tipo de ajuda ou cidade e vê do que cada uma precisa agora. Agricultores publicam o excedente ou a produção fora do padrão para doar ou vender a preço justo, e as ONGs próximas reservam e confirmam o recebimento (Colheita Solidária). Um painel público mostra o impacto da rede: kg salvos, famílias atendidas, renda gerada e ONGs ativas.

## 2. Atores e sistemas externos

| Ator/Sistema | Tipo | Como interage |
|---|---|---|
| Visitante | Pessoa | Navega sem conta: busca e lista de ONGs, página da ONG, ofertas sem distância nem contato, painel de impacto (UC-01, UC-13, UC-14) |
| Doador(a)/voluntário(a) | Pessoa | Conta logada: promete itens, se inscreve como voluntário, registra doação em dinheiro, acompanha contribuições (UC-05 a UC-07, UC-12). Camada 2 |
| Agricultor(a) familiar | Pessoa | Conta logada: publica e acompanha ofertas, vê o contato da ONG que reservou (UC-08, UC-11) |
| ONG / cozinha comunitária | Pessoa (conta da organização) | Conta logada: mantém o perfil, reserva ofertas, confirma recebimentos; na camada 2, gere necessidades e confirma doações (UC-03, UC-04, UC-09, UC-10) |
| Administrador(a) da plataforma | Pessoa do grupo | Usa só o admin do Django: aprova, reprova e desativa ONGs, mantém localidades e cadastros (RN-14, P-11) |
| Pix (fora do site) | Sistema externo, sem integração | O doador vê a chave Pix da ONG e paga por fora; o site só registra a promessa (D-27) |
| API pública de CNPJ | Sistema externo, opcional | Só se RF-35 for feito: consulta se o CNPJ existe e está ativo; a falha não bloqueia o cadastro (RNF-07) |
| servidor próprio (VPS) (Nginx do host, Docker, provedor de DNS, Let's Encrypt) | Infraestrutura | Hospeda a aplicação no subdomínio próprio do projeto; só Jimmie acessa (D-30) |
| GitHub (repositório e Actions) | Sistema externo de desenvolvimento | Guarda o código, recebe os pull requests e roda os testes de cada PR |

## 3. Fronteiras do sistema

**Dentro do sistema:** contas e perfis; localidades; ONGs, ODS e necessidades; ofertas, reservas e recebimentos; promessas, inscrições e doações em dinheiro (camada 2); painel de impacto; carga de dados de demonstração; admin do Django.

**Fora do sistema, mas interage com ele:** pagamento Pix (feito pelo doador fora do site), transporte e entrega da colheita (combinados entre ONG e agricultor pelo contato exibido), API de CNPJ (opcional), infraestrutura da VPS.

**Fora do escopo** (`requirements.md` §5): gateway de pagamento, geocodificação, e-mail de qualquer tipo, chat, logística, recuperação de senha, login social, mapas, app nativo, ONGs reais.

## 4. Visão de alto nível

Uma única aplicação Django que gera o HTML no servidor, atrás do Nginx do host, com um PostgreSQL próprio.

```text
Navegador (computador ou celular)
   │ HTTPS
   ▼
Nginx do host (servidor próprio) ──── /static/ e /media/ lidos direto do disco
   │ proxy_pass uma porta local reservada
   ▼
Container "app": Gunicorn + Django 5.2
   ├── core      settings, URLs, base.html, página inicial
   ├── contas    usuário, perfis, cadastro, login, localidades
   ├── ongs      ONG, ODS, necessidades, busca, lista, página
   ├── colheita  ofertas, reservas, recebimentos
   ├── doacoes   promessas, voluntariado, doação em dinheiro (camada 2)
   └── painel    indicadores e gráficos
   │ rede Docker interna
   ▼
Container "db": PostgreSQL 18
```

Na máquina dos devs, a mesma aplicação roda com `runserver` e SQLite.

## 5. Suposições e restrições herdadas

- **Equipe:** 4 devs (grupo Desenvolvimento) sem experiência presumida em Django; Jimmie monta o esqueleto, faz o deploy e revisa os PRs (D-29, D-30). Se a equipe mudar, o backlog muda.
- **Estratégia de entrega:** telas mock primeiro, banco por camadas; só a camada 1 é obrigatória com banco (D-28).
- **Hospedagem:** servidor próprio (VPS), porta reservada só em localhost, banco em rede interna, nada instalado no host, sem tocar o outro projeto do servidor (RNF-02, RNF-11). O desenho Django na VPS nunca foi testado; a primeira publicação no M2 valida isso (R-03).
- **Sem serviço externo obrigatório:** o sistema funciona sem nenhuma integração (D-27).
- **Sem usuários reais:** o volume de dados é o da carga de demonstração, sem requisito de desempenho ou escala.
- **Prazo:** apresentação em 10/11/2026 (P-10).

---
**Status**: [ ] Em andamento  [ ] Aguardando aprovação  [x] Aprovado em: 15/10/2026
