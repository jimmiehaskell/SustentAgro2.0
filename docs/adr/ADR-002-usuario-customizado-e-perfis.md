# ADR-002 — Modelo de usuário próprio desde o início, com perfis ligados a ele

## Status
Aceito (15/10/2026)

## Contexto
Há três perfis: doador/voluntário, agricultor e ONG. Uma conta de pessoa pode acumular doador e agricultor, mas a conta de ONG é só ONG (RN-12, D-15). Uma ONG pendente ou reprovada só acessa a "Minha conta" (RN-20). Trocar o modelo de usuário do Django depois que já existem migrations é caro, porque exige recriar o banco.

## Decisão
Criar no M1 o model `contas.Usuario` (herda de `AbstractUser`, com `AUTH_USER_MODEL = 'contas.Usuario'`) antes de qualquer migration. Ele tem um campo de tipo de conta (pessoa ou ONG). Os perfis ficam em models ligados por `OneToOneField`: `contas.PerfilPessoa` (marcações "é doador" e "é agricultor", telefone e localidade) e `ongs.Ong`. O login usa usuário e senha (RF-09), pelas views prontas do Django (`django.contrib.auth`).

## Alternativas consideradas
| Alternativa | Por que não foi escolhida |
|---|---|
| `User` padrão do Django, com o perfil só em models ligados | Funciona, mas impede acrescentar campos ao usuário depois sem uma migração difícil. A recomendação oficial do Django é criar um modelo próprio no início |
| Grupos e permissões do Django para os perfis | Servem para permissões, não para guardar dados do perfil (localidade, telefone, CNPJ); o acúmulo de perfis ficaria confuso |
| Um model de usuário por perfil | Impossibilita o acúmulo doador + agricultor numa mesma conta (RN-12) |

## Consequências
- O `db.sqlite3` atual e as migrations do app `ongs` atual são descartados. O projeto recomeça as migrations do zero no repositório novo (as 9 ONGs reais já saem do site, D-17).
- Toda view logada verifica o perfil por mixins comuns, feitos uma vez no esqueleto (por exemplo, `AgricultorRequeridoMixin` e `OngAtivaRequeridaMixin`).
- RF-08 (acúmulo de perfis, camada 3) passa a ser apenas marcar o segundo perfil em `PerfilPessoa`.

## Requisitos relacionados
RF-07, RF-08, RF-09, RF-11, RN-12, RN-20, RNF-05
