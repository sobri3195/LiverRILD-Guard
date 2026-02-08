# LiverRILD-Guard

**Author:** dr. Muhammad Sobri Maulana

LiverRILD-Guard adalah aplikasi prototipe **React + Python (Flask)** untuk memprediksi risiko
**Radiation-Induced Liver Disease (RILD)** pada pasien SBRT hati (HCC/metastasis) dengan variasi
fungsi hati (Child-Pugh/ALBI). Model menggabungkan parameter fungsi hati, laboratorium, serta
heterogenitas distribusi dosis untuk menghasilkan:

- Probabilitas kejadian RILD
- Probabilitas dekompensasi hati
- Estimasi overall survival (OS) 1 tahun
- Rekomendasi mitigasi (modifikasi rencana terapi/seleksi pasien)

## Struktur Proyek

- `app.py` → API backend Flask
- `frontend/` → aplikasi React (Vite)
- `requirements.txt` → dependensi backend

## Menjalankan Backend (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend berjalan di `http://localhost:8000`.

## Menjalankan Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend berjalan di `http://localhost:5173`.

## Endpoint API

### `GET /api/health`
Cek status layanan.

### `POST /api/predict`
Contoh payload:

```json
{
  "child_pugh": "A",
  "albi_score": -2.1,
  "bilirubin_mg_dl": 1.2,
  "albumin_g_dl": 3.8,
  "ast_u_l": 54,
  "alt_u_l": 49,
  "mean_liver_dose_gy": 15,
  "d700cc_gy": 11,
  "dose_heterogeneity_index": 1.2,
  "ptv_volume_cc": 340
}
```

## Catatan

Model pada repository ini adalah **decision-support prototype** untuk riset/eksplorasi awal,
bukan pengganti keputusan klinis final.
