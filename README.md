# ForestIA

Plataforma de simulaciones agrícolas: se cargan los datos de suelo (sustrato, humedad,
capa hídrica, clima, tipo de planta) y se genera una evolución predictiva (estadística)
de las plantas y de las capas que las contienen, considerando el consumo de nutrientes
de la especie cargada. Interfaz pensada para uso sin capacitación técnica.

## Stack

- **Django 5 + Django REST Framework** — backend y panel de administración
- **PostgreSQL/PostGIS** en producción (SQLite en desarrollo)
- **Celery + Redis** — simulaciones predictivas en segundo plano
- **Open-Meteo** — datos climáticos
- **Sondas IoT LoRaWAN + drones multiespectrales** — telemetría de suelo

## Estructura

```
config/            settings, urls, Celery
apps/
  dashboard/       panel principal (parcelas, clima, simulaciones, alertas)
  crops/           plantas y demandas nutricionales por etapa
  soils/           parcelas, perfiles edáficos y capas
  monitoring/      sondas, lecturas telemétricas y vuelos de drone
  weather/         registro climático + integración Open-Meteo
  simulation/      motor predictivo (biomasa, humedad, N) + tareas Celery
  alerts/          alertas agronómicas generadas por el modelo
  notifications/   canales de notificación (WhatsApp, Telegram, email)
fixtures/demo.json datos de ejemplo
docker-compose.yml despliegue de producción
```

## Arranque rápido (local)

```bash
# 1. Entorno virtual con nombre del proyecto
python3 -m venv venv-forestia
source venv-forestia/bin/activate
pip install -r requirements.txt

# 2. Variables de entorno
#    cp .env.example .env   # ya incluye una SECRET_KEY de desarrollo
#    Editar .env según necesidad (DEBUG, ALLOWED_HOSTS, DB_NAME, etc.)

python manage.py migrate
python manage.py loaddata fixtures/demo.json
python manage.py sync_weather --days 7
python manage.py createsuperuser

# Terminal 1: servidor web
python manage.py runserver

# Terminal 2: worker Celery (necesita Redis)
celery -A config worker -l info

# Terminal 3: programador de tareas periódicas (requiere Celery Beat)
celery -A config beat -l info
```

Panel principal: http://127.0.0.1:8000/  
Administración: http://127.0.0.1:8000/admin/  
API REST: http://127.0.0.1:8000/api/v1/

## Despliegue con Docker Compose (producción)

```bash
cp .env.example .env
# editar .env (producción)
docker compose up -d --build
```

Servicios levantados:
- **web**: Gunicorn + Django
- **db**: PostgreSQL con PostGIS
- **redis**: broker de Celery
- **worker**: tareas de simulación y sincronización
- **beat**: programador de tareas periódicas

Migraciones y fixture se aplican automáticamente al arrancar `web`.

> **Nota de Docker Desktop en macOS**: si el daemon está muy lento al iniciar,
> esperar a que la VM se estabilice antes de correr `docker compose up`.

## Flujo de uso

1. Cargar la parcela y su perfil de suelo (apps.soils).
2. Cargar la planta y sus etapas con demanda de nutrientes (apps.crops).
3. `python manage.py sync_weather` baja el pronóstico agro (ET0, lluvia, radiación) de Open-Meteo para las parcelas georreferenciadas.
4. Crear una simulación desde el **panel principal** (`/`) o vía POST a `/api/v1/simulation/runs/`.
5. Celery ejecuta el modelo (`apps/simulation/engine.py`) con el pronóstico real y guarda la serie en `result`.
6. El modelo genera alertas automáticas de riego y fertirrigación (apps.alerts).
7. La vista animada `/api/v1/simulation/runs/<id>/preview/` muestra la planta creciendo a tamaño referencial y las capas de suelo modificándose en el tiempo.

![Vista animada día 0](docs/vista_dia0.png)
![Vista animada día 80](docs/vista_dia80.png)

## Automatización (Celery Beat)

- **Clima cada 6 h** (minuto 17): sincroniza el pronóstico Open-Meteo de todas las parcelas.
- **Re-simulación diaria a las 05:23**: vuelve a correr la última simulación de cada parcela con el clima más reciente y regenera alertas.

## Notificaciones (WhatsApp listo para integrar)

Cada alerta generada se despacha por los canales activos (`apps.notifications`)
y queda registrada en `NotificationLog` con estado enviada / pendiente / fallida.
El canal de WhatsApp ya está cableado; para activarlo hay que:

1. Elegir proveedor (Meta WhatsApp Business Cloud API, Twilio, CallMeBot…).
2. Definir en el entorno: `WHATSAPP_TOKEN` (y `WHATSAPP_API_URL` si aplica).
3. Completar la llamada a la API en `apps/notifications/dispatchers.py` — el punto
   `TODO(integración)` está marcado.
4. Cargar el teléfono destino en la configuración JSON del canal (admin:
   "WhatsApp del productor" → `{"phone": "+549..."}`).

Hasta que se complete, los envíos quedan *pendientes* sin romper nada.

## Variables de entorno principales

```
SECRET_KEY=
DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=                  # vacío → SQLite; completar → PostgreSQL
DB_USER=forestia
DB_PASSWORD=forestia
DB_HOST=127.0.0.1
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
WHATSAPP_TOKEN=
WHATSAPP_API_URL=https://graph.facebook.com/v21.0
```

## Próximos pasos planificados

- Ingestión MQTT para sondas LoRaWAN
- Geometrías PostGIS (PointField / PolygonField)
- Calibración del modelo con datos reales de laboratorio
