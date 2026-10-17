#!/bin/sh
# Prepara a aplicação a cada início do container e depois executa o comando (Gunicorn)
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear -v 0

exec "$@"
