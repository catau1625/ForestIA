"""Corre una simulación predictiva de cultivo y devuelve la serie diaria.

Modelo simplificado (v1):
- Biomasa: crecimiento logístico con tasa y punto medio propios del cultivo.
- Humedad: balance hídrico con pulsos de riego cuando cae bajo el umbral,
  modulado por la retención del suelo.
- Nitrógeno: extracción lineal según demanda de la etapa activa.
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
IRRIGATION_DOSE_PCT = 8.0
STEP_DAYS = 3


def run_simulation(
    *,
    cycle_days: int,
    growth_rate: float,
    t_mid: int,
    nitrogen_demand: float,
    soil_type: str,
    initial_moisture_pct: float,
    initial_nitrogen_ppm: float,
    horizon_days: int,
) -> dict:
    """Genera las series diarias de biomasa, humedad y nitrógeno."""
    retention = SOIL_RETENTION.get(soil_type, 0.65)
    t, biomass, moisture, nitrogen = [], [], [], []
    current_moisture = initial_moisture_pct

    day = 0
    while day <= horizon_days:
        t.append(day)
        biomass.append(round(1 / (1 + math.exp(-growth_rate * (day - t_mid))), 4))
        moisture.append(round(current_moisture, 1))

        extraction = nitrogen_demand * min(1.0, day / max(1, cycle_days))
        nitrogen.append(round(max(0.0, initial_nitrogen_ppm * (1 - extraction)), 1))

        # Avance del balance hídrico hasta la próxima muestra
        for _ in range(STEP_DAYS):
            current_moisture -= nitrogen_demand * (1 - retention) * 0.35 * retention
            if current_moisture < IRRIGATION_THRESHOLD_PCT:
                current_moisture = initial_moisture_pct - IRRIGATION_DOSE_PCT
        current_moisture = max(5.0, current_moisture)
        day += STEP_DAYS

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
