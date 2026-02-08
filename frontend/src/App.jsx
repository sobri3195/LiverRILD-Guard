import { useState } from 'react'

const defaultForm = {
  child_pugh: 'A',
  albi_score: -2.1,
  bilirubin_mg_dl: 1.2,
  albumin_g_dl: 3.8,
  ast_u_l: 54,
  alt_u_l: 49,
  mean_liver_dose_gy: 15,
  d700cc_gy: 11,
  dose_heterogeneity_index: 1.2,
  ptv_volume_cc: 340
}

function App() {
  const [form, setForm] = useState(defaultForm)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const onChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({
      ...prev,
      [name]: name === 'child_pugh' ? value : Number(value)
    }))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      const data = await response.json()
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <h1>LiverRILD-Guard</h1>
      <p>
        Prediksi Radiation-Induced Liver Disease (RILD) pada pasien SBRT hati berbasis cadangan fungsi hati
        dan heterogenitas distribusi dosis.
      </p>

      <form className="grid" onSubmit={onSubmit}>
        <label>
          Child-Pugh
          <select name="child_pugh" value={form.child_pugh} onChange={onChange}>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
          </select>
        </label>

        {Object.entries(form)
          .filter(([key]) => key !== 'child_pugh')
          .map(([key, value]) => (
            <label key={key}>
              {key}
              <input
                name={key}
                type="number"
                step="0.1"
                value={value}
                onChange={onChange}
                required
              />
            </label>
          ))}

        <button type="submit" disabled={loading}>
          {loading ? 'Menghitung...' : 'Prediksi Risiko'}
        </button>
      </form>

      {result && (
        <section className="card">
          <h2>Hasil Prediksi</h2>
          <ul>
            <li>Tier risiko RILD: <strong>{result.risk_tier}</strong></li>
            <li>Probabilitas RILD: <strong>{Math.round(result.rild_probability * 100)}%</strong></li>
            <li>Probabilitas dekompensasi: <strong>{Math.round(result.decompensation_probability * 100)}%</strong></li>
            <li>Estimasi OS 1 tahun: <strong>{Math.round(result.overall_survival_1y * 100)}%</strong></li>
          </ul>
          <h3>Rekomendasi Mitigasi</h3>
          <ul>
            {result.mitigation_recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}

export default App
