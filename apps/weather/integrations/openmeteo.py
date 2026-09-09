"""Integración con Open-Meteo (gratuita, sin API key).

Documentación: https://open-meteo.com/en/docs
"""
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Variables agro relevantes. `et0_fao_evapotranspiration` viene en mm.
HOURLY = (
    "temperature_2m,relative_humidity_2m,wind_speed_10m,"
    "rain,shortwave_radiation,et0_fao_evapotranspiration"
)


def fetch_agro_weather(latitude: float, longitude: float, days: int = 7) -> list[dict]:
    """Devuelve una lista de registros horarios agro para un punto geográfico."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": HOURLY,
        "timezone": "auto",
        "forecast_days": days,
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()["hourly"]
    records = []
    for i, ts in enumerate(data["time"]):
        records.append(
            {
                "timestamp": ts,
                "temp_c": data["temperature_2m"][i],
                "humidity_pct": data["relative_humidity_2m"][i],
                "wind_ms": data["wind_speed_10m"][i],
                "rain_mm": data["rain"][i],
                "solar_radiation_mj": data["shortwave_radiation"][i],
                "et0_mm": data["et0_fao_evapotranspiration"][i],
            }
        )
    return records
