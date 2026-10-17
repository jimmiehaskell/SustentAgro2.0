#!/bin/bash
# Cria o banco e o usuário da aplicação na primeira inicialização do PostgreSQL (volume vazio).
# Depois disso, mudar DB_PASSWORD no .env não muda a senha no banco: use ALTER ROLE.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
     -v db_name="$DB_NAME" -v db_user="$DB_USER" -v db_password="$DB_PASSWORD" <<'SQL'
CREATE ROLE :"db_user" LOGIN PASSWORD :'db_password';
CREATE DATABASE :"db_name" OWNER :"db_user";
REVOKE ALL ON DATABASE :"db_name" FROM PUBLIC;
SQL
