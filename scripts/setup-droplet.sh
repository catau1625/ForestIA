#!/usr/bin/env bash
# Bootstrap de un Droplet nuevo en DigitalOcean para ForestIA.
# Ejecutar como root en el servidor (ej. vía SSH: ssh root@<IP> 'bash -s' < scripts/setup-droplet.sh).
set -e

echo "==> Actualizando sistema e instalando Docker"
apt-get update
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release git
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar Docker
systemctl enable docker
systemctl start docker

echo "==> Clonando ForestIA"
APP_DIR="/opt/forestia"
mkdir -p "$APP_DIR"
git clone https://github.com/catau1625/ForestIA.git "$APP_DIR" || true
cd "$APP_DIR"

echo "==> Creando .env de producción"
cp .env.example .env
# Valores mínimos para producción (editar SECRET_KEY y ALLOWED_HOSTS después)
sed -i 's/^DEBUG=.*/DEBUG=false/' .env
sed -i 's/^DB_HOST=.*/DB_HOST=db/' .env
sed -i 's/^DB_NAME=.*/DB_NAME=forestia/' .env
sed -i 's/^DB_USER=.*/DB_USER=forestia/' .env
sed -i 's/^DB_PASSWORD=.*/DB_PASSWORD=forestia/' .env
sed -i 's/^CELERY_BROKER_URL=.*/CELERY_BROKER_URL=redis:\/\/redis:6379\/0/' .env
sed -i 's/^CELERY_RESULT_BACKEND=.*/CELERY_RESULT_BACKEND=redis:\/\/redis:6379\/1/' .env

echo "==> Levantando servicios"
docker compose up -d --build

echo "==> Aplicando migraciones y fixture de demo"
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py loaddata fixtures/demo.json 2>/dev/null || true
docker compose exec -T web python manage.py collectstatic --noinput

echo "==> Listo. Accedé a http://$(curl -s ifconfig.me):8000"
