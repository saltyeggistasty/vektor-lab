# Loading Screen — Nabla Workspace

Loading screen ini **modular penuh**: mau nambah / ganti slide, cukup
taruh gambar di folder ini lalu edit `config.json`. Tidak perlu
menyentuh kode sama sekali.

## Cara nambah slide sendiri

1. Taruh gambarnya di folder `loading_screen/` ini (mis. `KOLAM.jpg`).
2. Buka `config.json`, tambahkan satu objek di dalam array `"slides"`:

```json
{
  "file": "KOLAM.jpg",
  "title": "Judul Slide",
  "subtitle": "Kalimat penjelas singkat di bawah judul.",
  "equation": "\\nabla\\cdot\\mathbf{F}\\;=\\;0",
  "credit": "Nabla Workspace"
}
```

3. Simpan, refresh browser. Selesai.

## Field yang tersedia

### Tiap slide
| Field       | Wajib? | Keterangan |
|-------------|--------|------------|
| `file`      | wajib  | Nama file di folder ini. Route hanya melayani ekstensi `.png .jpg .jpeg .webp .gif .json` |
| `title`     | opsional | Judul besar tengah-bawah |
| `subtitle`  | opsional | Kalimat kecil di bawah judul. Bisa memakai `\\(...\\)` untuk rumus inline |
| `equation`  | opsional | LaTeX penuh (one-line), di-render dengan KaTeX |
| `credit`    | opsional | Teks kecil kanan-bawah |
| `fit`       | opsional | `"cover"` (default, isi penuh) atau `"contain"` (utuh, ada pilar gelap) |
| `pos`       | opsional | Posisi fokus gambar, mis. `"center top"`, `"50% 30%"` |
| `drift_ms`  | opsional | Durasi animasi parallax slide ini (default 16000) |

### Global
| Field             | Default | Keterangan |
|-------------------|---------|------------|
| `rigged`          | `false` | **Mode presentasi.** `true` = loading selesai TEPAT pada `min_duration_ms`, hitungan asli diabaikan sepenuhnya. `false` = selesai saat hitungan beres + durasi minimum tercapai |
| `min_duration_ms` | `13000` | Luar loading. rigged: detik tepat berakhir; normal: batas minimum sebelum boleh berakhir |
| `slide_ms`        | `5500`  | Lama tiap gambar tampil sebelum fade ke gambar berikutnya |
| `fade_ms`         | `1400`  | Lama animasi crossfade antar gambar (0-1 dtk untuk snappy, 3-5 dtk untuk presentasi santai) |
| `max_wait_ms`     | `25000` | Batas keras untuk mode normal; diabaikan saat `rigged: true` |
| `shuffle`         | `false` | `true` = urutan slide diacak tiap reload |
| `status_initial` / `status_graph` / `status_physics` | - | Teks status di bawah bar |

### Mode presentasi (rigged)

Buat presentasi, isi begini: orang melihat art lebih dulu, "loading" tetap
tampil berapa lama pun yang kamu mau, lalu selesai TEPAT pada waktunya
meski perhitungan aslinya sudah beres sendirian di belakang layar (grafik
3D dan fisika quota tetap dihitung, jadi begitu loader hilang semuanya siap).

```json
{
  "rigged": true,
  "min_duration_ms": 45000,
  "slide_ms": 15000,
  "fade_ms": 3000
}
```

- `min_duration_ms` 45000 = loading tampil persis 45 detik.
- `slide_ms` 15000 = tiap gambar 15 detik (45/15 = 3 gantian, tiap slide
  kebagian selang-seling).
- `fade_ms` 3000 = crossfade antar gambar terasa lambat dan megah.

Tips: kalau kamu menaikkan `min_duration_ms`, naikkan `slide_ms` juga
supaya tiap gambar nongol cukup lama (raio kasar: min_duration_ms / slide_ms
= jumlah gantian; pilih ganjil supaya berakhir di gambar ke-1, genap
supaya berakhir di gambar ke-2).

## Sambil loading, app tetap disiapkan

Loader tidak hanya menunggu: grafik 3D bawaan dan simulasi fisika
Monte Carlo dihitung di belakang layar. Saat loading hilang,
`Grafik 3D` dan tab `Fisika` sudah siap.

## Tips gambar (laptop N4020 4GB)

- Pakai **JPG**, bukan PNG: sama efeknya, ukuran file dan waktu
  decode jauh lebih kecil.
- Rasio ideal **16:9** (mis. 1920x1080). Agar tidak terpotong-potong
  aneh saat di-cover, sisakan ruang aman di tepi.
- Berkas besar (>10MB) akan lama ter-decode di laptop kentang;
  loader sudah punya fallback bintang statis selama menunggu decode.
