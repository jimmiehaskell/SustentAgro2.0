# Imagem da aplicação (ADR-006): Django servido pelo Gunicorn (WSGI), sem linguagem no host
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Pastas montadas do host: estáticos (collectstatic) e uploads. Dono www-data (uid 33), como no servidor
RUN mkdir -p /app/staticfiles /app/storage/uploads \
    && chown -R www-data:www-data /app/staticfiles /app/storage \
    && chmod +x docker/entrypoint.sh

USER www-data

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saude/', timeout=4)" || exit 1

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30", \
     "--access-logfile", "-", "--error-logfile", "-"]
