#!/usr/bin/env bash
# Configura Nginx + Let's Encrypt (Certbot) para ForestIA en un Droplet.
# Requisito previo: el dominio ya debe apuntar al Droplet (registro A).
# Uso:
#   export DOMAIN=tufinca.com
#   bash <(curl -s https://raw.githubusercontent.com/catau1625/ForestIA/main/scripts/setup-https.sh)
set -e

DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-admin@$DOMAIN}"
# Dominios extra para el certificado (separados por espacio), ej. "www.midominio.com"
EXTRA_DOMAINS="${EXTRA_DOMAINS:-}"
# Orígenes permitidos para embeber la plataforma en iframes
FRAME_ANCESTORS="${FRAME_ANCESTORS:-https://katanacreacionesweb.cl https://www.katanacreacionesweb.cl}"

if [ -z "$DOMAIN" ]; then
  echo "ERROR: definí la variable de entorno DOMAIN antes de ejecutar."
  echo "Ejemplo: export DOMAIN=forestia.katanacreacionesweb.cl"
  exit 1
fi

EXTRA_FLAGS=""
for d in $EXTRA_DOMAINS; do
  EXTRA_FLAGS="$EXTRA_FLAGS -d $d"
done

echo "==> Instalando Nginx y Certbot"
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

echo "==> Configurando Nginx como proxy reverso para ForestIA"
cat > /etc/nginx/sites-available/forestia <<EOF
server {
    listen 80;
    server_name ${DOMAIN} ${EXTRA_DOMAINS};

    add_header Content-Security-Policy "frame-ancestors 'self' ${FRAME_ANCESTORS}" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /opt/forestia/staticfiles/;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/forestia /etc/nginx/sites-enabled/forestia

nginx -t
systemctl reload nginx

echo "==> Obteniendo certificado SSL con Let's Encrypt"
certbot --nginx -d "$DOMAIN" $EXTRA_FLAGS --non-interactive --agree-tos -m "$EMAIL" || true

echo "==> Habilitando firewall para HTTPS"
ufw allow 'Nginx Full' >/dev/null 2>&1 || true

echo "==> Listo. Accedé a https://${DOMAIN}"
echo "    El certificado se renueva automáticamente vía cron de Certbot."
