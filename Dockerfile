FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencias del sistema para psycopg (cliente PostgreSQL)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Estáticos sin necesidad de base de datos (los defaults de settings bastan)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Migrar y arrancar. El fixture es opcional (no falla si ya existe).
CMD sh -c "python manage.py migrate --noinput \
    && python manage.py loaddata fixtures/demo.json 2>/dev/null || true; \
    gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application"
