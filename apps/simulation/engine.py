"""Corre una simulación predictiva de cultivo y devuelve la serie diaria.

Modelo v2 — alimentado por clima real:
- Biomasa: crecimiento logístico con tasa y punto medio propios del cultivo.
- Humedad: balance hídrico diario. ETc = Kc(día) × ET0 pronosticada;
  entradas de lluvia y pulsos de riego según el umbral, modulados por
  la retención del suelo.
- Nitrógeno: extracción diaria según la demanda total del ciclo
  (suma de extracciones por etapa fenológica).
"""
import math

SOIL_RETENTION = {
    "franco": 0.85,
    "arenoso": 0.45,
    "arcilloso": 0.70,
    "fibra_coco": 0.75,
    "otro": 0.65,
}

IRRIGATION_THRESHOLD_PCT = 18.0
IRRIGATION_DOSE_PCT = 10.0
DEFAULT_ET0_MM = 4.5  # clima de relleno si no hay pronóstico cargado
MM_TO_PCT = 0.30      # mm de agua ≈ % de humedad en la zona radicular


def _kc_for_day(day: int, cycle_days: int, kc_i: float, kc_m: float, kc_f: float) -> float:
    """Interpolación por tramos del coeficiente de cultivo (FAO-56 simplificada)."""
    t = day / max(1, cycle_days)
    if t < 1 / 3:
        return kc_i + (kc_m - kc_i) * (t * 3)
    if t < 2 / 3:
        return kc_m
    return kc_m + (kc_f - kc_m) * ((t - 2 / 3) * 3)


def run_simulation(
    *,
    cycle_days: int,
    growth_rate: float,
    t_mid: int,
    nitrogen_demand_cycle_ppm: float,
    kc_initial: float,
    kc_mid: float,
    kc_end: float,
    soil_type: str,
    initial_moisture_pct: float,
    initial_nitrogen_ppm: float,
    horizon_days: int,
    weather_daily: list[dict] | None = None,
) -> dict:
    """Genera las series diarias de biomasa, humedad y nitrógeno.

    ``weather_daily`` es una lista opcional indexada por día con claves
    ``et0_mm`` y ``rain_mm`` (pronóstico Open-Meteo agregado por día).
    """
    retention = SOIL_RETENTION.get(soil_type, 0.65)
    daily_n_extraction = nitrogen_demand_cycle_ppm / max(1, cycle_days)

    t, biomass, moisture, nitrogen = [], [], [], []
    current_moisture = initial_moisture_pct
    current_nitrogen = initial_nitrogen_ppm

    for day in range(horizon_days + 1):
        # Clima del día: pronóstico real o relleno climatológico
        wx = (weather_daily or [{}] * (horizon_days + 1))[day] if weather_daily else {}
        et0 = wx.get("et0_mm") or DEFAULT_ET0_MM
        rain = wx.get("rain_mm") or 0.0

        # Biomasa (logística, porcentual 0–1)
        t.append(day)
        biomass.append(round(1 / (1 + math.exp(-growth_rate * (day - t_mid))), 4))

        # Balance hídrico del día
        kc = _kc_for_day(day, cycle_days, kc_initial, kc_mid, kc_end)
        current_moisture -= kc * et0 * MM_TO_PCT
        current_moisture += rain * MM_TO_PCT * retention
        if current_moisture < IRRIGATION_THRESHOLD_PCT:
            # pulso de riego que repone hasta capacidad de manejo
            current_moisture = initial_moisture_pct - IRRIGATION_DOSE_PCT
        current_moisture = max(5.0, min(60.0, current_moisture))
        moisture.append(round(current_moisture, 1))

        # Extracción de nitrógeno
        current_nitrogen = max(0.0, current_nitrogen - daily_n_extraction)
        nitrogen.append(round(current_nitrogen, 1))

    return {
        "days": t,
        "biomass": biomass,
        "moisture_pct": moisture,
        "nitrogen_ppm": nitrogen,
        "final": {
            "biomass": biomass[-1],
            "moisture_pct": moisture[-1],
            "nitrogen_ppm": nitrogen[-1],
        },
    }
