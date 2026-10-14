from __future__ import annotations

DEFAULT_IDEAL = {
    "N": (40, 80),
    "P": (40, 80),
    "K": (40, 80),
    "ph": (6.0, 7.5),
}

CROP_IDEALS: dict[str, dict[str, tuple[float, float]]] = {
    "rice": {"N": (80, 120), "P": (40, 60), "K": (40, 60), "ph": (5.5, 7.0)},
    "wheat": {"N": (80, 120), "P": (40, 60), "K": (30, 50), "ph": (6.0, 7.5)},
    "maize": {"N": (80, 120), "P": (40, 70), "K": (40, 70), "ph": (5.8, 7.0)},
    "cotton": {"N": (100, 140), "P": (40, 70), "K": (40, 70), "ph": (5.8, 8.0)},
    "coffee": {"N": (80, 120), "P": (20, 40), "K": (80, 140), "ph": (6.0, 6.5)},
    "apple": {"N": (20, 40), "P": (120, 145), "K": (180, 210), "ph": (5.5, 6.8)},
    "banana": {"N": (80, 120), "P": (70, 95), "K": (45, 55), "ph": (5.5, 7.0)},
    "grapes": {"N": (10, 30), "P": (120, 145), "K": (190, 210), "ph": (5.5, 7.0)},
    "mango": {"N": (15, 35), "P": (20, 40), "K": (25, 40), "ph": (5.5, 7.5)},
    "orange": {"N": (15, 30), "P": (5, 20), "K": (5, 15), "ph": (5.5, 7.0)},
    "papaya": {"N": (40, 70), "P": (50, 70), "K": (45, 55), "ph": (6.0, 6.5)},
    "pomegranate": {"N": (15, 30), "P": (15, 30), "K": (35, 50), "ph": (5.5, 7.2)},
    "watermelon": {"N": (90, 120), "P": (5, 20), "K": (45, 55), "ph": (5.5, 6.8)},
    "muskmelon": {"N": (90, 120), "P": (5, 20), "K": (45, 55), "ph": (6.0, 7.0)},
    "coconut": {"N": (15, 30), "P": (125, 150), "K": (190, 210), "ph": (5.2, 6.5)},
    "jute": {"N": (70, 90), "P": (40, 60), "K": (35, 45), "ph": (6.0, 7.5)},
    "lentil": {"N": (10, 30), "P": (55, 80), "K": (15, 25), "ph": (6.0, 7.0)},
    "blackgram": {"N": (30, 50), "P": (55, 80), "K": (15, 25), "ph": (6.2, 7.2)},
    "mungbean": {"N": (15, 30), "P": (40, 60), "K": (15, 25), "ph": (6.2, 7.2)},
    "mothbeans": {"N": (15, 30), "P": (40, 60), "K": (15, 30), "ph": (6.0, 7.5)},
    "pigeonpeas": {"N": (15, 30), "P": (55, 80), "K": (15, 30), "ph": (5.5, 7.0)},
    "kidneybeans": {"N": (15, 30), "P": (55, 80), "K": (15, 25), "ph": (5.5, 6.5)},
    "chickpea": {"N": (30, 50), "P": (55, 80), "K": (75, 85), "ph": (6.0, 7.5)},
    "potato": {"N": (80, 120), "P": (50, 80), "K": (80, 120), "ph": (5.0, 6.5)},
    "tomato": {"N": (80, 120), "P": (40, 70), "K": (40, 80), "ph": (6.0, 7.0)},
    "onion": {"N": (60, 100), "P": (40, 70), "K": (40, 70), "ph": (6.0, 7.0)},
    "soybean": {"N": (20, 40), "P": (40, 70), "K": (30, 60), "ph": (6.0, 7.0)},
    "barley": {"N": (50, 90), "P": (30, 50), "K": (30, 50), "ph": (6.0, 7.5)},
}


def _status(value: float, low: float, high: float) -> str:
    if value < low:
        return "deficient"
    if value > high:
        return "excess"
    return "optimal"


def recommend_fertilizer(crop: str, n: float, p: float, k: float, ph: float) -> dict:
    crop_key = crop.strip().lower().replace(" ", "_")
    ideals = CROP_IDEALS.get(crop_key, DEFAULT_IDEAL)
    readings = {"N": n, "P": p, "K": k, "ph": ph}
    actions = {
        "N": {
            "deficient": "Apply Urea (46-0-0) to raise nitrogen.",
            "excess": "Reduce nitrogen fertilizer; consider a split application next cycle.",
            "optimal": "Nitrogen is within range — maintain current N practice.",
        },
        "P": {
            "deficient": "Apply DAP (18-46-0) to raise phosphorus.",
            "excess": "Skip P fertilizer this cycle; excess P can lock micronutrients.",
            "optimal": "Phosphorus is within range — maintain current P practice.",
        },
        "K": {
            "deficient": "Apply MOP / Muriate of Potash (0-0-60) to raise potassium.",
            "excess": "Avoid extra potash this cycle.",
            "optimal": "Potassium is within range — maintain current K practice.",
        },
        "ph": {
            "deficient": "Soil is acidic — apply agricultural lime to raise pH.",
            "excess": "Soil is alkaline — apply gypsum (and organic matter) to lower pH.",
            "optimal": "pH is within range — no lime/gypsum needed.",
        },
    }

    trace = []
    recommendations = []
    for nutrient, (low, high) in ideals.items():
        value = readings[nutrient]
        status = _status(value, low, high)
        reason = (
            f"{nutrient}={value:.2f} vs ideal {low}-{high} for {crop_key} -> {status}"
        )
        action = actions[nutrient][status]
        trace.append(
            {
                "nutrient": nutrient,
                "value": value,
                "ideal_low": low,
                "ideal_high": high,
                "status": status,
                "triggered": status != "optimal",
                "reason": reason,
            }
        )
        if status != "optimal":
            recommendations.append(action)

    if not recommendations:
        recommendations.append(
            "Soil N/P/K/pH are within the ideal band for this crop. No correction needed."
        )

    return {
        "method": "rule-based",
        "label": "Rule-Based — no ML accuracy applicable",
        "crop": crop_key,
        "recommendations": recommendations,
        "primary_action": recommendations[0],
        "trace": trace,
    }
