from dataclasses import dataclass
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@dataclass
class PatientInput:
    child_pugh: str
    albi_score: float
    bilirubin_mg_dl: float
    albumin_g_dl: float
    ast_u_l: float
    alt_u_l: float
    mean_liver_dose_gy: float
    d700cc_gy: float
    dose_heterogeneity_index: float
    ptv_volume_cc: float


def _child_pugh_weight(value: str) -> float:
    mapping = {"A": 0.1, "B": 0.35, "C": 0.65}
    return mapping.get(value.upper(), 0.25)


def _risk_tier(score: float) -> str:
    if score < 0.35:
        return "Rendah"
    if score < 0.65:
        return "Sedang"
    return "Tinggi"


def calculate_risk(payload: PatientInput) -> Dict[str, object]:
    liver_reserve_component = (
        (payload.albi_score + 2.0) / 2.5
        + (payload.bilirubin_mg_dl / 3.0)
        + max(0.0, (4.0 - payload.albumin_g_dl) / 2.0)
        + _child_pugh_weight(payload.child_pugh)
    ) / 4.0

    inflammation_component = ((payload.ast_u_l / 120.0) + (payload.alt_u_l / 120.0)) / 2.0

    dose_component = (
        (payload.mean_liver_dose_gy / 30.0)
        + (payload.d700cc_gy / 20.0)
        + (payload.dose_heterogeneity_index / 2.0)
        + (payload.ptv_volume_cc / 900.0)
    ) / 4.0

    rild_probability = min(
        0.95,
        max(
            0.03,
            0.48 * liver_reserve_component
            + 0.18 * inflammation_component
            + 0.34 * dose_component,
        ),
    )

    decomp_probability = min(0.95, max(0.02, rild_probability * 0.82 + 0.08))
    os_1y_probability = max(0.2, min(0.98, 0.91 - (rild_probability * 0.42) - (decomp_probability * 0.18)))

    mitigations: List[str] = []
    if rild_probability >= 0.65:
        mitigations.extend(
            [
                "Pertimbangkan reduksi mean liver dose dan re-optimasi distribusi dosis untuk menurunkan hotspot.",
                "Evaluasi ulang kelayakan SBRT (fraksinasi lebih konservatif atau pendekatan alternatif).",
                "Konsultasi hepatologi sebelum terapi untuk optimalisasi fungsi hati.",
            ]
        )
    elif rild_probability >= 0.35:
        mitigations.extend(
            [
                "Gunakan adaptive planning bila terjadi perubahan volume hati/target.",
                "Perketat monitoring lab hati mingguan selama dan setelah SBRT.",
            ]
        )
    else:
        mitigations.append("Lanjutkan dengan constraint DVH ketat dan monitoring rutin pasca terapi.")

    return {
        "risk_tier": _risk_tier(rild_probability),
        "rild_probability": round(rild_probability, 3),
        "decompensation_probability": round(decomp_probability, 3),
        "overall_survival_1y": round(os_1y_probability, 3),
        "mitigation_recommendations": mitigations,
    }


@app.get("/api/health")
def health() -> object:
    return jsonify({"status": "ok", "service": "LiverRILD-Guard"})


@app.post("/api/predict")
def predict() -> object:
    data = request.get_json(force=True)
    patient = PatientInput(
        child_pugh=data["child_pugh"],
        albi_score=float(data["albi_score"]),
        bilirubin_mg_dl=float(data["bilirubin_mg_dl"]),
        albumin_g_dl=float(data["albumin_g_dl"]),
        ast_u_l=float(data["ast_u_l"]),
        alt_u_l=float(data["alt_u_l"]),
        mean_liver_dose_gy=float(data["mean_liver_dose_gy"]),
        d700cc_gy=float(data["d700cc_gy"]),
        dose_heterogeneity_index=float(data["dose_heterogeneity_index"]),
        ptv_volume_cc=float(data["ptv_volume_cc"]),
    )
    return jsonify(calculate_risk(patient))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
