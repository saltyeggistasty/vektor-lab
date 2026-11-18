# ∇ Nabla Workspace.

## Kumpulan alat-alat berat matematika dan fisika.

### Tugas Mata Kuliah Rekayasa Perangkat Lunak
### Nama: Afif Sheva Ramdhani
### NIM : 41257083
### Kelas : 1A-2025


## Jalankan
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Buka http://127.0.0.1:5000 (butuh internet untuk memuat Plotly dari CDN).

## Fitur
- **Kalkulator**: gradien, turunan parsial (orde 1–6), Laplacian, Hessian, turunan berarah,
  divergensi, curl, Jacobian + evaluasi di titik tertentu.
- **Grafik 3D**: permukaan z=f(x,y) (+ medan gradien), medan vektor 3D, kurva parametrik r(t).
- **Fisika ⚡ (baru)**: simulasi Monte Carlo fluks listrik pada manifold z=f(x,y) —
  permukaan & medan bebas, satuan SI penuh (m, N/C, Φ dalam N·m²/C, Q=ε₀Φ dalam C),
  grafik 3D densitas-fluks + vektor fluks lokal + titik sampel MC, katalog 5 preset,
  pop-up "?" ELI5 di tiap parameter, dan asisten AI (OpenRouter) yang menerjemahkan
  deskripsi bebas menjadi konfigurasi simulasi tervalidasi.

### Tab Fisika (monte carlo flux)
```
Φ = ∬_D F(x, y, f(x,y)) · (−f_x, −f_y, 1) dx dy  ≈  (Luas domain) · mean(g),   g = −P·f_x − Q·f_y + R
```
- Medan seragam (E₀ dalam N/C + arah), muatan titik (E = kQ/r²), atau `custom`: P,Q,R bebas
  fungsi x,y,z (satuan N/C). Lihat `physics.py` untuk detail satuan & metode.
- Konfigurasi LLM ada di `config.json` (`openrouter_api_key`, `model`, `fallback_models`).
  Browser memanggil `/api/physics/ai` → backend chat completions OpenRouter → JSON
  tervalidasi (rumus di-parse & di-clamp, AI tidak menyuntik kode) → form terisi otomatis.
- **Interpretasi hasil oleh AI**: setelah tiap simulasi (toggle `pai`), angka hasil MC
  dikirim ke `/api/physics/interpret` → tutor AI menulis penjelasan ELI5 + analogi
  dunia nyata berdasarkan angka sebenarnya (flux, Q terkurung, error, suku integrand),
  ditampilkan di kartu "Hasil Simulasi".

SymEngine hanya menyediakan `diff`, `Matrix`, `Lambdify`, dst., jadi operator vektornya
(grad, div, curl, Laplacian, Hessian, Jacobian, directional) ditulis sendiri di `vectorcalc.py`.

Sintaks: `x^2*y`, `sin(x)*cos(y)`, `exp(-x^2-y^2)`, `sqrt(x^2+y^2)`. Variabel: x, y, z (kurva: t).

## Struktur
- `app.py` – route Flask/API · `vectorcalc.py` – logika matematika · `physics.py` – modul fisika
  (Monte Carlo fluks + glue AI OpenRouter) · `templates/`, `static/` – UI (`physics.js` = tab fisika,
  `app.js` = kalkulator + grafik umum) · `config.json` – kunci API LLM (jangan dibagikan!)
