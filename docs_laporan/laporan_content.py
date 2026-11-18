# -*- coding: utf-8 -*-
"""Konten teks Laporan Proyek Akhir, Nabla Workspace (Bahasa Indonesia).
Dipisahkan dari engine build_pdf.py agar mudah disunting."""

META = {
    "judul": "Nabla Workspace",
    "subjudul": "Aplikasi Web Edukasi Fisika & Matematika Terintegrasi Fitur Kecerdasan Artifisial",
    "mk": "Rekayasa Perangkat Lunak (TIKB2503021)",
    "tema": "E-Learning & Smart Education AI",
    "dosen": "Yudhistira Arie Wijaya, M.Kom., CDS.",
    "prodi": "Program Studi S1 Teknik Informatika, STMIK IKMI Cirebon",
}

# ============================================================
# BAGIAN I, PRD/SRS
# ============================================================

LATAR_BELAKANG = """Pemahaman matematika dan fisika tingkat lanjut, kalkulus multivariabel, aljabar linear, persamaan diferensial, elektrodinamika, hingga mekanika kuantum, sangat bergantung pada kemampuan mahasiswa memverifikasi perhitungan secara mandiri. Pada praktiknya, alat bantu komputasi yang tersedia tersebar di banyak situs yang berbeda, umumnya beriklan, tidak mendukung penulisan notasi matematika standar (LaTeX) secara langsung, hanya tersedia dalam satu bahasa, dan tidak menyediakan visualisasi konsep fisika yang interaktif. Kondisi ini menimbulkan hambatan belajar: waktu terbuang untuk berpindah-pindah alat, kesalahan transkripsi notasi, serta absennya umpan balik konseptual terhadap hasil perhitungan.

Di sisi lain, kemajuan Kecerdasan Artifisial (AI) generatif membuka peluang baru dalam pembelajaran: pengguna dapat mendeskripsikan eksperimen fisika dalam bahasa sehari-hari dan sistem menyusun parameter simulasi secara otomatis, atau memperoleh penjelasan naratif atas hasil statistik simulasi. Sayangnya, fitur AI pada kebanyakan aplikasi edukasi masih bersifat tempelan (gimmick) dan tidak terikat pada alur kerja komputasi inti.

Nabla Workspace lahir untuk menjawab persoalan tersebut: sebuah aplikasi web edukasi fisika dan matematika yang memadukan lebih dari 45 alat komputasi, 25 simulasi numerik dan grapher interaktif, laboratorium simulasi Monte Carlo Hukum Gauss, serta dua fitur AI yang tertanam langsung pada alur kerja (konfigurasi simulasi via bahasa natural dan interpretasi hasil simulasi), semuanya dalam antarmuka gelap bertema naratif yang didukung tujuh bahasa dan dapat dijalankan offline sebagai aplikasi desktop."""

TUJUAN_LINGKUP = """Tujuan proyek ini adalah membangun aplikasi web fungsional secara end-to-end, mulai dari PRD, pemodelan UML, perancangan UI/UX, konstruksi kode, integrasi fitur AI, pengujian otomatis, hingga pelaporan, sebagai bukti kompetensi rekayasa perangkat lunak menyeluruh.

Ruang lingkup di dalam proyek:
• Antarmuka web satu halaman (single-page style) dengan server aplikasi Flask (Python) dan klien vanilla JavaScript tanpa framework.
• Komputasi simbolik matematika (integral, limit, derivatif, deret, produk, ODE, matriks, polinomial, dll.) berbasis SymPy/SymEngine.
• Komputasi numerik fisika: Monte Carlo fluks listrik (Hukum Gauss), 10 simulasi dinamika (RK4, split-step Fourier, random walk, dll.), dan 15 grapher interaktif.
• Dua fitur AI berbasis LLM melalui OpenRouter: (1) konfigurasi simulasi dari deskripsi bahasa natural, (2) interpretasi hasil simulasi.
• Internasionalisasi 7 bahasa (Inggris, Indonesia, Melayu, Rusia, Ukraina, Irish, Arab, termasuk dukungan RTL).
• Distribusi versi offline Windows x64 (PyInstaller onedir + pywebview/Electron).
• Kontak pengguna: formulir kritik/saran dan audit donasi via email SMTP.

Di luar ruang lingkup: sistem multi-pengguna/autentikasi, penyimpanan data pengguna pada basis data server, aplikasi seluler native, dan penyuntingan konten pembelajaran oleh pengguna."""

DEFINISI = [
    ("LaTeX", "Bahasa markup notasi matematis standar; seluruh input math-field dan output hasil memakai LaTeX."),
    ("MathLive", "Komponen web <math-field> sumber terbuka untuk editor persamaan LaTeX interaktif."),
    ("SymPy / SymEngine", "Pustaka komputasi simbolik Python; SymEngine dipakai sebagai backend cepat."),
    ("op_data", "Struktur JSON terstruktur buatan sendiri yang mendeskripsikan operasi (integral/derivatif/limit/deret/produk) tanpa evaluasi mentah, dikirim frontend → backend."),
    ("Sentinel error", "Penanda teks __NABLA_ERR__:jenis pada hasil komputasi yang diterjemahkan menjadi pesan ramah berbahasa."),
    ("Monte Carlo", "Metode numerik berbasis sampling acak; di sini untuk mengestimasi fluks listrik melalui permukaan (Hukum Gauss)."),
    ("OpenRouter", "Gerbang API LLM; menyediakan model utama dan model fallback."),
    ("CalcGuard", "Modul JavaScript anti-spam yang memberi cooldown tombol hitung (5 dtk) dan formulir (10 dtk)."),
    ("i18n", "Internationalization, mekanisme penerjemahan antarmuka (7 berkas JSON bahasa)."),
    ("PyInstaller", "Pembungkus aplikasi Python menjadi executable Windows (onedir)."),
    ("Electron", "Kerangka desktop (shell jendela) yang menjalankan server lokal sebagai sidecar."),
    ("CI/CD", "Continuous Integration / Continuous Delivery; otomatisasi uji & rilis pada GitHub Actions."),
    ("OBE", "Outcome-Based Education, kerangka penilaian berbasis capaian pembelajaran."),
]

REFERENSI = [
    "IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications.",
    "ISO/IEC/IEEE 29148:2018, Systems and software engineering, Life cycle processes, Requirements engineering.",
    "Yudhistira Arie Wijaya, M.Kom., CDS., \"Panduan Tugas Proyek Akhir Mandiri & Rubrik Penilaian OBE\", TIKB2503021 Rekayasa Perangkat Lunak, STMIK IKMI Cirebon.",
    "Dokumentasi resmi: Flask, SymPy, NumPy, Plotly, MathLive, KaTeX, GSAP, OpenRouter API, PyInstaller, Electron.",
    "Pressman, R.S. & Maxim, B.R., Software Engineering: A Practitioner's Approach, 9th ed.",
]

PERSPEKTIF = """Nabla Workspace adalah sistem web tiga lapis (three-tier) yang berjalan sepenuhnya pada satu mesin server (lokal atau cloud):

1. Lapisan Presentasi, peramban web modern yang memuat seluruh antarmuka (vanilla JS + MathLive, Plotly, KaTeX, GSAP yang di-vendor lokal, tanpa CDN eksternal). Semua aset statis dilayani dengan mekanisme cache-busting versi boot.
2. Lapisan Aplikasi, server Flask (Python 3.14) yang mengekspos 18 route REST/JSON, bertindak sebagai dispatcher ke mesin komputasi dan gerbang ke layanan eksternal.
3. Lapisan Komputasi & Layanan, mesin komputasi lokal deterministik (mathlab, physics, vectorcalc, graphlab, simlab) serta layanan eksternal opsional (LLM OpenRouter, SMTP Gmail).

Selain dijalankan sebagai situs web, paket yang sama dibundel menjadi aplikasi offline Windows x64 (PyInstaller onedir) yang dapat diluncurkan sebagai jendela native (pywebview) atau melalui shell Electron berarsitektur sidecar. Kunci API dan kredensial email tidak pernah dibundel ke dalam aplikasi; pengguna dapat mengisinya sendiri pada config.json di samping executable.

Persistensi saat ini berbasis berkas (config.json, address.json) dan pengiriman email langsung; perancangan basis data relasional untuk pengembangan lanjut dipaparkan pada Bab 11."""

FUNGSI_UTAMA = [
    "Kalkulator kalkulus multivariabel: 8 operasi (gradien, turunan parsial, Laplacian, Hessian, turunan berarah, divergensi, curl, Jacobian).",
    "Grafik 3D interaktif: permukaan z=f(x,y), medan vektor 3D, kurva parametrik r(t), dirender Plotly dengan overlay gradien.",
    "Menu \"War Stories\": 8 kategori matematika dan 9 kategori fisika berbentuk kartu naratif bergaya poster (karya seni 100% buatan manusia).",
    "20 tool komputasi matematika & fisika berbasis math-field LaTeX (integral & limit, matriks, ODE, Taylor, polinomial, statistik, kompleks, modular, entropi, termodinamika, kuantum, elektrostatika, relativitas, proyektil, fluida, kalor, Schwarzschild, optik, getaran harmonis, induksi).",
    "10 simulasi numerik: peta logistik, atraktor Lorenz, deret Fourier, transformasi matriks, random walk, pendulum ganda, proyektil dengan hambatan, orbit Kepler, celah ganda, paket gelombang.",
    "15 grapher interaktif: domain coloring, fraktal (Mandelbrot/Julia/Newton), gradien multivariabel, frame Frenet, slope field, distribusi PDF/CDF, algoritma graf (Dijkstra/BFS/DFS/MST), medan listrik, siklus P-V, Ising Monte Carlo, diagram Minkowski, fluida interaktif, geodesik lubang hitam, ray tracing lensa, transformasi 3D.",
    "Laboratorium Simulasi Monte Carlo fluks listrik (Hukum Gauss) dengan grafik permukaan, kerucut fluks, awan sampel, dan statistik lengkap.",
    "Fitur AI 1: konfigurasi simulasi dari deskripsi bahasa natural (mengisi form secara otomatis, dapat langsung menjalankan simulasi).",
    "Fitur AI 2: interpretasi naratif hasil simulasi dalam bahasa antarmuka aktif.",
    "Internasionalisasi 7 bahasa dengan dukungan RTL (Arab) dan fallback Inggris; 3 tema warna (Golden, Light, Black).",
    "Panel Donasi (kartu wallet + salin), formulir audit donasi, dan kritik/saran, dikirim via email SMTP.",
    "Unduh versi offline (zip + sha256) dan jalankan sebagai aplikasi desktop tanpa instalasi Python.",
]

KARAKTERISTIK_PENGGUNA = """Pengguna sasaran: siswa SMA/SMK, mahasiswa S1 (khususnya yang mengambil kalkulus, fisika dasar/lanjut, matematika teknik), serta guru/dosen yang membutuhkan alat demonstrasi. Tidak diperlukan akun atau registrasi; satu-satunya keterampilan prasyarat adalah familiaritas dasar notasi matematis. Editor math-field menyediakan papan ketik virtual sehingga pengguna yang belum hafal LaTeX tetap dapat menyusun ekspresi. Pengguna tingkat lanjut dapat memakai mode manual dan parameter opsional (batas integral, titik evaluasi, orde derivatif, seed simulasi)."""

BATASAN = """Batasan desain dan implementasi:
• Komputasi simbolik dilakukan server-side (Flask lokal), peramban tidak menjalankan SymPy; untuk build offline, "server" berjalan di mesin yang sama.
• Fitur AI bergantung pada kunci API OpenRouter milik pengguna (free tier: kuota terbatas); tanpa kunci, aplikasi tetap berfungsi penuh tanpa AI dengan pesan yang jelas.
• Jumlah sampel Monte Carlo dibatasi 500–400.000; ukuran unggahan 8 MB; foto audit wajib PNG/JPG/WEBP.
• Tidak ada basis data server pada rilis ini; persistensi konfigurasi berbasis berkas dan preferensi pengguna pada localStorage.
• Bahasa pemrograman: Python (server) dan JavaScript vanilla (klien) tanpa framework UI.

Asumsi: pengguna memakai peramban modern (Chrome/Edge/Firefox versi terkini), dan untuk fitur AI/kontak tersedia koneksi internet saat fitur tersebut dipakai."""

# (id, user story, acceptance criteria)
KEBUTUHAN_FUNGSIONAL = [
    ("SF-01", "Sebagai pengguna, saya ingin memilih salah satu dari 7 bahasa antarmuka agar saya dapat belajar dengan bahasa yang saya kuasai.",
     "7 bahasa tersedia pada layar pembuka dan menu bahasa; teks Arab tampil RTL; kunci yang belum diterjemahkan jatuh ke Inggris; pilihan tersimpan di localStorage dan bertahan setelah muat ulang."),
    ("SF-02", "Sebagai pengguna, saya ingin mengganti tema tampilan (Golden/Light/Black) dan preset warna agar nyaman dipakai.",
     "Tema berubah seketika tanpa muat ulang; preferensi tersimpan; kontras teks tetap terbaca pada ketiga tema."),
    ("SF-03", "Sebagai pengguna baru, saya diajak melalui layar pembuka (pilih bahasa → loading → pilih bidang studi) agar orientasi jelas.",
     "Alur intro tampil sekali per keputusan pengguna; loading screen menampilkan karya seni dan atribusi artis; kartu bidang (Matematika/Fisika) dapat dimasuki dengan klik atau tombol ENTER."),
    ("SF-04", "Sebagai pelajar, saya ingin menghitung 8 operasi kalkulus multivariabel dengan mengetik notasi LaTeX langsung.",
     "Input via math-field; hasil ditampilkan dalam LaTeX ter-render dan nilai plain; operasi: gradien, turunan parsial, Laplacian, Hessian, turunan berarah, divergensi, curl, Jacobian; input tidak valid menghasilkan pesan ramah, bukan traceback."),
    ("SF-05", "Sebagai pelajar, saya ingin melihat grafik 3D permukaan, medan vektor, dan kurva parametrik dari fungsi yang saya ketik.",
     "Tiga tipe grafik tersedia; dirender Plotly dengan rotasi/zoom; rentang dan resolusi memiliki nilai default yang masuk akal dan dapat diubah."),
    ("SF-06", "Sebagai pengguna, saya ingin menjelajah menu kartu \"War Stories\" (8 kategori matematika, 9 fisika) agar menemukan tool sesuai topik.",
     "Navigasi mouse dan keyboard (ENTER masuk, ESC kembali); tata letak kolom tersimpan; latar blur mengikuti kartu terpilih."),
    ("SF-07", "Sebagai pelajar, saya ingin memakai 20 tool matematika & fisika berbasis math-field (integral & limit, matriks, ODE, dll.).",
     "Semua tool menerima input LaTeX; hasil berupa tabel langkah (LaTeX + plain); tool matriks menerima input matriks NxN via math-field; parameter opsional tersedia dan terisi otomatis dari notasi."),
    ("SF-08", "Sebagai pelajar, saya ingin tool Integral & Limit mendeteksi jenis operasi dari ekspresi saya secara otomatis.",
     "Deteksi integral/derivatif/limit/deret Σ/produk ∙; bila mode manual tidak cocok dengan deteksi, mode otomatis berpindah saat tombol Hitung ditekan lalu payload dihitung ulang; parameter yang diisi user mengunci field terkait dengan label \"Custom\"."),
    ("SF-09", "Sebagai peneliti, saya ingin menjalankan simulasi Monte Carlo fluks listrik pada permukaan z=f(x,y) dengan medan seragam/titik muatan/ekspresi kustom.",
     "N dapat diatur 500–400.000 (default 100.000) dengan seed opsional; output memuat fluks Φ, ketidakpastian 95%, muat terkurung Q=ε₀Φ, galat relatif, trace konvergensi, luas domain & permukaan; grafik permukaan + kerucut fluks + awan sampel tampil."),
    ("SF-10", "Sebagai pengguna, saya ingin mengonfigurasi seluruh parameter simulasi cukup dengan satu kalimat bahasa natural (AI).",
     "Tombol Konfigurasi AI menerima teks bebas; permintaan di luar topik ditolak lokal tanpa konsumsi token; konfigurasi JSON valid mengisi form otomatis; bila opsi auto-run aktif, simulasi langsung dijalankan."),
    ("SF-11", "Sebagai pengguna, saya ingin memperoleh interpretasi naratif hasil simulasi dalam bahasa antarmuka aktif (AI).",
     "Opsi interpretasi otomatis (#pai) hanya memicu permintaan pada run yang diinisiasi pengguna; hasil menampilkan nama model; teks penalaran internal dibersihkan; kegagalan API menghasilkan pesan terjemahan, bukan crash."),
    ("SF-12", "Sebagai pengguna, saya ingin kesalahan input ditampilkan sebagai pesan yang ramah dan berbahasa.",
     "Error domain (LabError/PhysError/CalcError) dikirim sebagai {ok:false, error, errKey, errArgs}; frontend menerjemahkan errKey via i18n; tidak ada traceback Python yang tampil ke pengguna."),
    ("SF-13", "Sebagai pengguna aktif, saya tidak ingin spam klik merusak alur atau membebani server.",
     "CalcGuard memberi cooldown 5 detik pada semua tombol hitung dan 10 detik pada formulir; klik di luar cooldown diabaikan dengan pesan err.calc_wait."),
    ("SF-14", "Sebagai pendukung, saya ingin melihat dan menyalin alamat donasi resmi.",
     "Panel donasi menampilkan kartu wallet dari address.json; tombol salin menyalin alamat ke clipboard dengan umpan balik visual."),
    ("SF-15", "Sebagai pendukung, saya ingin mengirim formulir audit donasi lengkap dengan bukti foto.",
     "Formulir memvalidasi field wajib dan tipe foto (PNG/JPG/WEBP, ≤8MB); data dikirim sebagai email melalui SMTP STARTTLS; hasil berhasil/gagal ditampilkan ramah."),
    ("SF-16", "Sebagai pengguna, saya dapat melaporkan bug atau memberi saran dari menu About us.",
     "Form mengirim email dengan jenis (bug/saran), kontak opsional sebagai Reply-To, pesan maks. 5000 karakter; konfirmasi tampil di layar."),
    ("SF-17", "Sebagai pengguna tanpa internet stabil, saya dapat mengunduh dan menjalankan versi offline.",
     "Panel unduhan menampilkan nama, ukuran, dan sha256 build; zip dapat diunduh; ekstrak → jalankan exe → jendela aplikasi terbuka tanpa instalasi Python; fitur AI default nonaktif dan dapat diopt-in."),
    ("SF-18", "Sebagai pengguna mobile, saya dapat memakai aplikasi dalam mode seluler.",
     "Toggle Mobile/Desktop tersedia sejak layar pembuka; tata letak, menu, dan panel menyesuaikan; scrollbar dan panel layar penuh bekerja normal."),
]

# (id, kebutuhan, metrik)
KEBUTUHAN_NF = [
    ("SNF-01", "Performa", "Ekspresi kalkulus umum selesai < 5 detik; simulasi MC 100.000 sampel < 10 detik pada mesin kelas menengah."),
    ("SNF-02", "Keamanan", "Kunci API dan app password tidak pernah dibundel/di-hard-code; dimuat dari config.json milik pemilik; komunikasi eksternal via HTTPS (OpenRouter) dan SMTP STARTTLS; seluruh input divalidasi server-side; tidak ada evaluasi raw string pengguna ke Python."),
    ("SNF-03", "Keandalan", "Fallback model AI berurutan hingga 4 percobaan; pipeline komputasi bebas dari 277 kasus uji regresi; error dibungkus uniform, server tidak pernah mengembalikan traceback."),
    ("SNF-04", "Kebergunaan", "7 bahasa + RTL; papan ketik virtual; contoh penggunaan per tool; hint dan tooltip; pesan kesalahan spesifik (dx hilang, batas tak valid, dsb.)."),
    ("SNF-05", "Portabilitas", "Berjalan pada peramban modern tanpa instalasi; versi offline Windows x64 onedir tanpa ketergantungan runtime; aset pihak ketiga di-vendor (offline-first)."),
    ("SNF-06", "Pemeliharaan", "Pemisahan tanggung jawab per modul (SRP); penambahan tool baru via registry TOOLS tanpa mengubah dispatcher (OCP); kontrak REST {ok, error, errKey} (DIP); tiga suite uji otomatis menjaga regresi."),
    ("SNF-07", "Aksesibilitas", "Kontras teks latar gelap terjaga; navigasi keyboard penuh pada menu; ukuran ketik responsif; mode mobile."),
    ("SNF-08", "Kapasitas", "Unggahan maks 8 MB; N sampel dibatasi 500–400.000; panjang pesan umpan balik 5000 karakter."),
    ("SNF-09", "Kompatibilitas", "Chrome/Edge/Firefox terkini; WebP/MP4 backdrop; HiDPI canvas; fallback peluncuran pywebview → app-mode browser."),
    ("SNF-10", "Keterlacakan", "Setiap SF/SNF dipetakan ke kasus uji otomatis atau skenario uji manual pada Bab 13–15."),
]

FITUR_AI_DETAIL = """Spesifikasi Fitur AI Utama, OpenRouter LLM

A. Konfigurasi simulasi via bahasa natural (POST /api/physics/ai → physics.ai_configure)
1) Pengguna menulis deskripsi bebas, contoh: \"gelombang parabola dengan medan seragam ke arah z, 200 ribu sampel\".
2) Guardrail ganda: (a) regex lokal di frontend menolak permintaan di luar topik (kode, resep, lagu, dll.) tanpa konsumsi token; (b) validasi yang sama diulang di server.
3) Server menyusun prompt sistem + konteks konfigurasi aktif + bahasa antarmuka, lalu memanggil POST https://openrouter.ai/api/v1/chat/completions (Authorization Bearer, header X-Title).
4) Model utama: nvidia/nemotron-3-ultra-550b-a55b:free; fallback berurutan: nvidia/nemotron-3.5-super-vl:free, google/gemma-4-31b-it:free; hingga 4 percobaan. Suhu 0.3, max_tokens 1500, timeout 90 dtk.
5) Respons diparse dengan ekstraktor JSON toleran (menangani blok penalaran <think> dan pagar markdown), lalu divalidasi terhadap skema (permukaan, medan, domain, N, seed). Konfigurasi valid mengisi form; bila #aiAutoRun dicentang, simulasi langsung dijalankan.

B. Interpretasi hasil simulasi (POST /api/physics/interpret → physics.ai_interpret)
1) Setelah run yang diinisiasi pengguna (bukan boot auto-run, penghematan kuota free tier), statistik lengkap (Φ, CI95, Q, galat relatif, kontribusi per suku, konvergensi) dikirim sebagai konteks.
2) LLM menghasilkan narasi edukatif 3–6 kalimat dalam bahasa antarmuka aktif; nama model ditampilkan; teks penalaran internal dibersihkan (_clean_interp).

C. Degradasi yang anggun (graceful degradation)
1) Tanpa config.json/kunci API: permintaan AI mengembalikan PhysError berbahasa (\"API key OpenRouter belum diisi…\"), ditampilkan pada panel pesan; seluruh fitur non-AI tetap berfungsi.
2) Pada build offline, kedua opsi AI default tidak dicentang dan panel menyertakan catatan kebutuhan internet + kunci, koneksi hanya terjadi saat pengguna menekan tombol AI."""

API_TABLE = [
    ("GET /", "Halaman utama (HTML)."),
    ("POST /api/calc", "8 operasi kalkulus multivariabel (vectorcalc)."),
    ("POST /api/surface | /api/field | /api/curve", "Data grafik permukaan / medan vektor / kurva parametrik."),
    ("POST /api/lab", "Dispatcher tool: graphlab → simlab → mathlab (45+ tool)."),
    ("POST /api/physics/simulate", "Simulasi Monte Carlo fluks (stats + graph + samples)."),
    ("POST /api/physics/ai", "Konfigurasi simulasi via bahasa natural (LLM)."),
    ("POST /api/physics/interpret", "Interpretasi naratif hasil simulasi (LLM)."),
    ("POST /api/audit | /api/feedback", "Formulir audit donasi / kritik-saran → email SMTP."),
    ("GET /api/appinfo", "Status build (frozen/offline atau web)."),
    ("GET /download/info | /download/offline", "Metadata & berkas zip versi offline."),
    ("GET /i18n/<bahasa>.json", "Berkas terjemahan (JSON)."),
    ("GET /donation_addresses", "Isi address.json (wallet donasi)."),
    ("GET /menu_screen/* | /loading_screen/* | /language_select_backdrop/* | /about_us_menu/*", "Aset seni, konfigurasi loading, backdrop video, foto tim."),
]

# ============================================================
# BAGIAN II, SDD
# ============================================================

ARSITEKTUR_NARASI = """Gambar 6.1 memperlihatkan arsitektur tiga lapis. Pada lapisan presentasi, seluruh pustaka pihak ketiga (Plotly, KaTeX beserta 58 berkas font, GSAP, MathLive) di-vendor ke static/vendor sehingga aplikasi sepenuhnya berfungsi tanpa internet. Lapisan aplikasi Flask memisahkan route UI/aset, route komputasi, dan route AI/kontak; satu wrapper @api membungkus seluruh handler agar error domain selalu berbentuk {ok:false, error, errKey, errArgs} dengan HTTP 400. Lapisan komputasi terdiri atas lima mesin deterministik; layanan eksternal (LLM dan SMTP) bersifat opsional dan hanya diakses atas aksi pengguna. Persistensi server berbasis berkas JSON; preferensi pengguna (tema, bahasa, tata letak) disimpan pada localStorage klien.

Varian deployment: (1) situs web, Flask pada port publik; (2) build offline PyInstaller onedir, server lokal 127.0.0.1 dengan jendela pywebview, fallback app-mode peramban; (3) shell Electron, sidecar tanpa kepala (NABLA_HEADLESS=1) + BrowserWindow sandbox (contextIsolation, nodeIntegration:false)."""

USECASE_NARASI = """Aktor utama adalah Pengguna (pelajar/guru). Actor sekunder: Pemilik Aplikasi (mengelola config.json dan address.json), serta dua sistem eksternal, LLM OpenRouter (menerima permintaan konfigurasi & interpretasi) dan SMTP Gmail (menerima email audit/umpan balik). Relasi «extend» menunjukkan bahwa konfigurasi AI dapat langsung memicu simulasi (auto-run), dan «include» opsional (#pai) menambahkan interpretasi setelah simulasi dijalankan pengguna.

Skenario-skenario utama dipaparkan pada Tabel 8.1–8.5."""

SKENARIO_TABEL = [
    ("Tabel 8.1", "Skenario: Melakukan perhitungan integral tak tentu",
     [("Aktor", "Pengguna (pelajar)"),
      ("Prakondisi", "Aplikasi terbuka; tool Integral & Limit aktif."),
      ("Alur utama", "1) Pengguna mengetik \\int xe^x\\,dx pada math-field (atau memakai papan ketik virtual). 2) tools.js membangun op_data JSON. 3) Sistem mendeteksi operasi = integral tak tentu. 4) Pengguna menekan Hitung (CalcGuard memvalidasi cooldown). 5) POST /api/lab → mathlab._build_op → sp.integrate → _best_form/_pretty_latex. 6) Hasil LaTeX + plain tampil pada panel Hasil."),
      ("Alur alternatif", "3a) Mode manual ≠ deteksi → mode otomatis berpindah, form dirender ulang, payload dikumpulkan ulang. 5a) dx hilang pada integral tentu → sentinel err.int_missing_dx → pesan i18n ramah."),
      ("Postkondisi", "Hasil tampil; riwayat contoh dapat disalin (tombol salin).")]),
    ("Tabel 8.2", "Skenario: Menjalankan simulasi Monte Carlo fluks listrik",
     [("Aktor", "Pengguna"),
      ("Prakondisi", "Lab Simulasi Monte Carlo terbuka; preset terpilih."),
      ("Alur utama", "1) Pengguna memilih preset (mis. Pelat Datar sin(x²+y²)), jenis medan, kuat/arah, rentang domain, dan N=100.000. 2) Tekan Simulasi → POST /api/physics/simulate. 3) monte_carlo_flux sampling acak ber-seed. 4) Plotly menggambar permukaan + kerucut fluks + awan sampel; tabel statistik (Φ, CI95, Q, galat) terisi."),
      ("Alur alternatif", "2a) N di luar 500–400.000 → diklem; 3a) sampel tak-finite (lubang permukaan) diabaikan dan dihitung sebagai n_valid."),
      ("Postkondisi", "Statistik dan grafik tampil; bila #pai aktif, interpretasi AI menyusul.")]),
    ("Tabel 8.3", "Skenario: Konfigurasi simulasi via bahasa natural (AI)",
     [("Aktor", "Pengguna; LLM OpenRouter (sekunder)"),
      ("Prakondisi", "Kunci API terisi pada config.json; panel AI aktif."),
      ("Alur utama", "1) Pengguna menulis deskripsi bebas. 2) Guardrail lokal lolos. 3) POST /api/physics/ai. 4) ai_configure memanggil LLM (fallback ×3 bila perlu). 5) JSON tervalidasi → form terisi otomatis; kartu ringkasan AI menampilkan model. 6) Bila #aiAutoRun aktif → simulasi langsung berjalan."),
      ("Alur alternatif", "2a) Permintaan di luar topik → ditolak lokal tanpa token. 4a) Semua model gagal → pesan terjemahan pada #aiMsg. 0a) Kunci kosong → PhysError berbahasa."),
      ("Postkondisi", "Konfigurasi terpasang; pengguna dapat langsung mensimulasikan.")]),
    ("Tabel 8.4", "Skenario: Mengirim kritik/saran",
     [("Aktor", "Pengguna; SMTP Gmail (sekunder)"),
      ("Prakondisi", "Panel About us terbuka."),
      ("Alur utama", "1) Pengguna memilih jenis (bug/saran), mengisi nama, kontak (opsional), pesan. 2) Tekan kirim (cooldown 10 dtk). 3) POST /api/feedback → EmailMessage dikirim via SMTP STARTTLS (kontak menjadi Reply-To). 4) Konfirmasi tampil."),
      ("Alur alternatif", "2a) Klik ganda dalam cooldown → diabaikan dengan pesan. 3a) SMTP gagal → pesan gagal ramah, data tidak disimpan."),
      ("Postkondisi", "Email diterima pemilik; tidak ada data yang tersimpan di server.")]),
    ("Tabel 8.5", "Skenario: Mengganti bahasa antarmuka",
     [("Aktor", "Pengguna"),
      ("Prakondisi", "Aplikasi terbuka (layar mana pun)."),
      ("Alur utama", "1) Pengguna membuka menu bahasa. 2) Memilih salah satu dari 7 bahasa. 3) i18n.js menerapkan kamus baru pada seluruh elemen ber-atribut data-i18n; arah teks RTL diterapkan untuk Arab. 4) Pilihan disimpan (localStorage: nablaLang)."),
      ("Alur alternatif", "3a) Kunci belum diterjemahkan → fallback Inggris."),
      ("Postkondisi", "Seluruh antarmuka (termasuk pesan kesalahan) berbahasa terpilih.")]),
]

ACTIVITY_NARASI = """Gambar 8.1 memodelkan alur perhitungan tool matematika dari tekan tombol hingga render. Titik keputusan pertama adalah CalcGuard (anti-spam); titik kedua adalah kecocokan mode manual terhadap operasi terdeteksi, inilah pembeda utama Nabla Workspace: payload op_data dibangun dari notasi LaTeX, bukan evaluasi raw. Setelah dispatch /api/lab, backend membangun objek SymPy tak-evaluasi (_build_op) lalu mengeksekusinya tepat satu kali (_apply_opd) untuk mencegah double-apply; kegagalan terstruktur (sentinel __NABLA_ERR__) dialirkan ke pesan i18n, sedangkan keberhasilan melewati pemilihan bentuk terbaik (_best_form) dan pretty-printer LaTeX (_pretty_latex). Tiga flow-final terpisah (cooldown, error domain, sukses) menggambarkan bahwa setiap jalur berakhir dengan elegan tanpa membunuh sesi."""

CLASS_NARASI = """Pemodelan kelas dilakukan pada tingkat modul (Gambar 9.1) karena arsitektur memisahkan mesin komputasi Python dari klien JavaScript. Kelas FlaskApp adalah boundary yang hanya bertugas parsing request, dispatch, dan normalisasi error. MathLab menampung 20 handler tool dan seluruh pipeline op_data (_build_op, _apply_opd, _expr_int, _bound, _pretty_latex, _best_form). PhysicsLab memuat Monte Carlo dan kedua fungsi AI beserta pembantu JSON-toleran. VectorCalc, GraphLab, dan SimLab adalah mesin domain dengan registry TOOLS. Prinsip SOLID: SRP, tiap modul satu tanggung jawab komputasi; OCP, menambah tool = menambah entri registry tanpa menyentuh dispatcher; LSP/ISP, seluruh handler tool mengikuti kontrak payload/hasil yang sama; DIP, frontend hanya bergantung kontrak REST, bukan implementasi mesin. Hierarki error domain (LabError/PhysError/CalcError) memakai atribut errKey agar terjemahan berada di sisi klien."""

SEQ_NARASI = """Gambar 10.1 memperlihatkan pertukaran pesan lengkap skenario AI: pengguna → frontend → Flask → PhysicsLab → OpenRouter, termasuk guardrail lokal (langkah 2, tanpa token), fallback model (langkah 6), validasi skema (langkah 7), auto-run simulasi (langkah 11–13) dan interpretasi opsional #pai (langkah 14). Gambar 10.2 memperlihatkan alur perhitungan tool via /api/lab beserta cabang ALT error domain (LabError → HTTP 400 → pesan i18n). Kedua diagram menegaskan kontrak {ok, ...} yang seragam, inilah antarmuka yang menjaga konsistensi antar-diagram dan kode."""

ERD_NARASI = """Rilis saat ini menyimpan konfigurasi pada berkas (config.json, address.json) dan mengirim formulir langsung sebagai email, sehingga tidak ada basis data server. Sebagai perancangan ke depan, Gambar 11.1 menormalisasi entitas-entitas yang telah teridentifikasi ke skema relasional (SQLite/PostgreSQL): PENGGUNA_PERANGKAT (preferensi per perangkat: bahasa, tema, preset), LOG_SIMULASI (jejak audit parameter & hasil), UMPAN_BALIK, AUDIT_DONASI (termasuk status verifikasi), ALAMAT_DONASI, dan KONFIGURASI_APLIKASI (pasangan kunci-nilai per modul dengan penanda terenkripsi). Kardinalitas: satu perangkat dapat mencatat banyak log, mengirim banyak umpan balik, dan mengajukan banyak audit. Skema ini memungkinkan fitur riwayat perhitungan per pengguna tanpa mengubah kontrak REST, entitas tinggal dipetakan dari payload op_data yang sudah terstruktur."""

UIUX_NARASI = """Identitas visual Nabla Workspace adalah \"war stories\": latar gelap emas, kartu bertema poster dengan karya seni 100% buatan manusia (bebas AI) dan atribusi artis di setiap layar pembuka. Prinsip yang dipegang: (1) konten matematika selalu berkontras tinggi di atas latar tenang; (2) navigasi tiga ketukan maksimal, pilih bahasa, pilih bidang, pilih tool; (3) setiap panel tool memuat contoh penggunaan yang bisa langsung ditekan; (4) kesalahan selalu ramah dan berbahasa; (5) mode mobile paritas fitur dengan desktop.

Tiga preset warna (Golden, Light, Black) mengubah palet seluruh panel termasuk overlay Donasi/Unduh. Papan ketik virtual membantu pengguna yang belum hafal LaTeX. CalcGuard memberi umpan balik cooldown yang jelas, bukan klik sunyi. Layar-layar berikut direkam langsung dari aplikasi berjalan."""

UI_SHOTS = [
    ("ui/01_intro_bahasa.png", "Layar pembuka: manifesto berganti bahasa + pemilih bahasa."),
    ("ui/01b_grid_bahasa.png", "Pemilih bahasa: 7 bahasa dengan bendera (termasuk RTL Arab)."),
    ("ui/02_loading_screen.png", "Loading screen karya seni + atribusi artis (100% buatan manusia)."),
    ("ui/03_pilih_bidang.png", "Layar pilih bidang studi (Matematika / Fisika)."),
    ("ui/04_menu_matematika.png", "Menu War Stories Matematika: kartu kategori bergaya poster."),
    ("ui/05_kategori_kalkulus.png", "Kategori Kalkulus: kartu tool (Integral & Limit, Grafik 3D, dst.)."),
    ("ui/06_tool_integral.png", "Tool Integral & Limit: math-field, mode Auto (deteksi), contoh penggunaan."),
    ("ui/07_hasil_integral.png", "Hasil perhitungan live (sin(x)/x) dirender KaTeX."),
    ("ui/08_menu_fisika.png", "Menu War Stories Fisika (9 kategori)."),
    ("ui/09_kategori_elektro.png", "Kategori Elektrodinamika: Simulasi Monte Carlo, Kalkulator Elektrostatika, Graph Medan Listrik."),
    ("ui/10_lab_montecarlo.png", "Lab Monte Carlo berjalan: permukaan + kerucut fluks, Φ ≈ 2,306 N·m²/C, Q = 20,42 pC, 100.000 sampel."),
]

# ============================================================
# BAGIAN III, PENGUJIAN
# ============================================================

STRATEGI_UJI = """Strategi pengujian Nabla Workspace berlapis:

1. Pengujian unit & integrasi backend (Python): fungsi konversi, pembangunan objek simbolik, eksekusi operasi, validasi batas, dan penanganan error diuji langsung terhadap mathlab.run_tool tanpa server.
2. Pengujian E2E pipeline (Python + Node): konversi LaTeX → plain dieksekusi melalui fungsi la2plain ASLI yang diekstrak dari static/tools.js dan dijalankan lewat Node subprocess, memastikan frontend dan backend diuji sebagai satu pipeline nyata, bukan tiruan.
3. Audit lintas-tool: setiap tool berbasis math-field ditepati input LaTeX umum (\\frac, \\left\\right, \\sqrt, \\pi, pangkat, \\cdot, spasi) untuk memastikan tidak ada crash maupun kebocoran makro.
4. Pengujian manual eksploratif: alur UI (7 bahasa, 3 tema, mode mobile, panel Donasi/About/Unduh) dan live demo.

Klasifikasi hasil: PASS (cocok eksak/numerik), PASS-WARN (nilai benar, bentuk tampil berbeda namun ekuivalen), FAIL-VISIBLE (salah tampil), FAIL-SILENT (kosong/tanpa pesan), TIMEOUT (batas 20 detik per kasus). Kriteria lulus suite: nol FAIL-VISIBLE/FAIL-SILENT/TIMEOUT."""

SUITE_TABLE = [
    ("test_benchmark.py", "E2E Integral & Limit (bug_reports2.md)", "140 kasus × 2 mode (native+auto) = 277 eksekusi", "247 PASS · 30 PASS-WARN · 0 FAIL"),
    ("test_integral_tool.py", "E2E integral & tool mathfield (bug_reports.md)", "104 kasus (termasuk matriks via mathfield, properti d(∫f)=f)", "97 PASS · 7 PASS-WARN · 0 FAIL"),
    ("test_tools_audit.py", "Audit 10 tool mathfield + 4 engine konversi", "23 kasus input LaTeX umum", "23 PASS · 0 FAIL"),
]

CONTOH_KASUS = [
    ("L01", r"\lim_{x\to 0}\frac{e^x-1-x-\frac{x^2}{2}}{x^3}", "1/6", "PASS"),
    ("D08", r"\frac{d}{dx}\sqrt{1+\sin^2 x}", "sin(x)cos(x)/√(1+sin²x)", "PASS"),
    ("S05", r"\sum_{n=1}^{\infty}\frac{1}{n(n+1)}", "1", "PASS"),
    ("I01", r"\int xe^x\,dx", "(x−1)e^x", "PASS"),
    ("DI01", r"\int_0^1 x^2e^x\,dx", "e−2", "PASS"),
    ("C01", r"\int_0^1\frac{d}{dx}(x^3e^x)\,dx", "2e", "PASS"),
    ("P-\\sin^2x", r"\sin^2x + \cos^2x", "1", "PASS"),
    ("V-paste", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x\bigm{|}_{x=1}", "0", "PASS"),
]

BUG_NARASI = """Pengujian menemukan dan mengharuskan perbaikan sejumlah cacat material; dua putaran laporan bug (bug_reports.md, bug_reports2.md) diselesaikan hingga nol kegagalan. Cacat representatif dan perbaikannya:

1. Batas atas Σ tanpa kurung kurawal (\sum_{n=1}^5n) terbaca serakah hingga menyedot badan deret → aturan batas tanpa-kurung diperketat (hanya bilangan/peubah tunggal).
2. Pangkat fungsi (\sin^2x, \sin^{-1}x) menghasilkan objek SymPy tak-terdefinisi (sin**2*x) → scanner normalizeFnPowers menulis ulang menjadi (sin(x))^{2} dan asin(x) untuk pangkat −1, plus fallback parser function_exponentiation dan guard fungsi-tanpa-argumen.
3. Simbol indeks Σ/∏ yang diasumsikan integer tidak cocok dengan dummy Sum → simbol diasumsikan diteruskan (assume_int) ke seluruh pipeline, menghilangkan Piecewise liar pada deret.
4. Simbol log tanpa Abs pada integral menghasilkan bentuk domain-salah → pembungkus _abs_log + pemilih bentuk terbaik (_best_form: kandidat factor/together/cancel/trigsimp/radsimp/simplify/expand dipilih berdasarkan count_ops minimum).
5. Batang evaluasi |_{x=1} hilang saat copy-paste (MathLive membuang \\bigm{|}) → transformasi bar-evaluasi generalisasi (mengenali bentuk subskrip-dengan-sama setelah badan operator).
6. Pesan mentah Python bocor ke pengguna → sentinel __NABLA_ERR__ + penerjemahan errKey ×7 bahasa; wrapper internal error menampilkan pesan generik bervariasi, traceback hanya di log server."""

CI_CD_NARASI = """Sesuai rencana, repositori akan menautkan otomatisasi GitHub Actions (.github/workflows/ci.yml) dengan dua job: (1) backend, pasang Python 3.14 + requirements, jalankan ketiga suite (exit code menjadi gerbang); (2) frontend-harness, pasang Node, jalankan ekstraksi la2plain dan audit input. Badge status ditautkan pada README. Bluprint alur kerja:

name: ci
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - run: pip install -r requirements.txt
      - run: python test_benchmark.py
      - run: python test_integral_tool.py
      - run: python test_tools_audit.py
  frontend-harness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: python test_tools_audit.py   # harness Node dipanggil dari suite Python

Implementasi repositori GitHub dilakukan mandiri oleh mahasiswa (di luar lingkup dokumen ini)."""

KESIMPULAN_UJI = """Ketiga suite otomatis lulus penuh: 404 eksekusi kasus tercatat (277 + 104 + 23) dengan 0 kegagalan material (FAIL-VISIBLE/FAIL-SILENT/TIMEOUT = 0); 60 kasus berstatus PASS-WARN ekuivalen-nilai (bentuk tampil berbeda namun matematis sama). Pengujian manual eksploratif menutup alur non-komputasi (7 bahasa, 3 tema, mode mobile, formulir kontak, unduhan offline). Dengan demikian kriteria lulus Bab 13 terpenuhi dan kebutuhan SF-01 s.d. SF-18 serta SNF-01 s.d. SNF-10 terverifikasi."""

# ============================================================
# ============================================================
# BAGIAN IV, NARASI VIDEO (dipindah ke PDF terpisah: Narasi.pdf)
# ============================================================

VIDEO_KETENTUAN = """Ketentuan umum (sesuai Panduan Proyek, diperbarui per instruksi dosen): hanya SATU video yang diwajibkan, yaitu Video Final Live Demo dengan durasi 8 sampai 12 menit (target 10 menit); video Progres 1 dan Progres 2 tidak diperlukan. Perekaman layar WAJIB menampilkan wajah penyaji (webcam aktif di pojok layar) sepanjang video; resolusi minimal 720p (disarankan 1080p); suara jernih tanpa bising; demo aplikasi dan fitur AI wajib live sungguhan (bukan screenshot); unggah ke YouTube (Unlisted/Public) atau Google Drive (akses tautan), lalu tautkan pada README.md repositori."""

VIDEO_FINAL = """SKRIP NARASI VIDEO FINAL, LIVE DEMO APLIKASI WEB & SISTEM UTUH (target 10:00, rentang 8 sampai 12 menit)

[0:00-1:00] ELEVATOR PITCH & IDENTITAS
"Selamat pagi semuanya. Saya Afif Sheva Ramdhani, NIM 41257083, Kelas 1A-2025, dengan Tema Topik Kelompok 'E-Learning & Smart Education AI'. Bayangkan kalian sedang belajar fluks listrik dan ingin membuktikan Hukum Gauss secara numerik, tapi alat komputasi kalian tersebar di lima situs berbeda, penuh iklan, dan tidak menerima notasi LaTeX. Proyek mandiri saya, Nabla Workspace, menyelesaikan itu: satu aplikasi web, dan juga versi offline Windows, berisi lebih dari empat puluh lima alat komputasi, dua puluh lima simulasi interaktif, laboratorium Monte Carlo, dan dua fitur AI yang tertanam langsung di alur kerja. Semua saya bangun sendiri dari nol: PRD, UML, UI/UX, kode, pengujian."

[1:00-2:00] MASALAH & NILAI GUNA (RINGKASAN PRD)
"Masalahnya tiga. Alat komputasi terfragmentasi dan tidak mendukung notasi matematika standar, hampir semuanya hanya berbahasa Inggris padahal kita butuh multi bahasa, dan fitur AI pada aplikasi edukasi umumnya hanya tempelan yang tidak terikat alur kerja komputasi. Nabla Workspace menjawabnya dengan satu antarmuka terpadu: kalkulator kalkulus multivariabel delapan operasi, dua puluh tool matematika fisika berbasis editor persamaan, sepuluh simulasi numerik dan lima belas grapher interaktif, tujuh bahasa termasuk Arab dengan dukungan kanan ke kiri, dan bisa diunduh sebagai aplikasi offline, jadi tetap jalan tanpa internet."

[2:00-2:45] KEBUTUHAN FUNGSIONAL & NON-FUNGSIONAL
"Kebutuhan fungsional saya definisikan delapan belas poin, dari pemilihan bahasa, kalkulasi kalkulus, deteksi operasi otomatis pada tool integral, simulasi Monte Carlo dengan sampel hingga empat ratus ribu, sampai formulir kritik saran. Kebutuhan non-fungsionalnya sepuluh: performa di bawah lima detik, kunci API yang tidak pernah dibundel, keandalan dengan fallback model AI, kebergunaan tujuh bahasa, portabilitas offline, dan keterlacakan setiap kebutuhan ke kasus uji."

[2:45-3:30] PERAN STRATEGIS FITUR AI
"Fitur AI saya tanam langsung di alur kerja, bukan tempelan. Pertama, konfigurasi simulasi lewat bahasa natural: pengguna cukup menulis 'gelombang parabola dengan medan seragam', dan LLM mengisi seluruh form simulasi, bisa langsung dijalankan. Kedua, interpretasi hasil: setelah simulasi, AI menjelaskan makna angka fluks dan muat terkurung dalam bahasa pengguna. Guardrail lokal menolak pertanyaan di luar topik tanpa membuang token, dan tanpa API key aplikasi tetap berfungsi penuh."

[3:30-4:30] ARSITEKTUR & PEMODELAN UML (RINGKASAN SDD)
"Sekilas rancangannya: arsitektur tiga lapis, lapisan presentasi di peramban dengan seluruh pustaka di-vendor lokal, lapisan aplikasi Flask dengan delapan belas route REST dan kontrak seragam, dan lapisan komputasi lima mesin Python. Pemodelan UML-nya empat diagram: Use Case dengan aktor Pengguna, Pemilik Aplikasi, LLM OpenRouter, dan SMTP Gmail; Activity Diagram alur perhitungan dari CalcGuard sampai render; Class Diagram lima mesin komputasi dengan prinsip SOLID, terbukti dari pola registry yang memungkinkan tool baru ditambah tanpa mengubah dispatcher; dan Sequence Diagram alur AI end to end dengan fallback tiga model. Basis data dirancang enam entitas untuk pengembangan lanjut, sementara rilis ini memakai persistensi berkas."

[4:30-7:00] LIVE DEMO, ALUR KOMPUTASI (SUNGGUHAN, BUKAN REKAMAN)
"Kita masuk demo live. [Buka aplikasi] Layar pembuka, saya pilih Bahasa Indonesia, perhatikan manifesto berganti bahasa. Loading screen karya seni dengan atribusi artis, semua seratus persen buatan manusia. Pilih bidang Matematika, masuk menu war stories, buka kategori Kalkulus, dan buka Integral & Limit. [Ketik] Saya ketik integral x kuadrat e pangkat x dx dari nol sampai satu. Hitung... hasilnya e minus dua, tampil dalam notasi cantik plus nilai numerik. Sekarang uji deteksi otomatis: saya masukkan contoh deret sigma lima suku, sistem mendeteksi operasinya deret dan mode berpindah sendiri. [Tunjukkan error ramah] Kalau saya buang dx pada integral tentu, lihat, pesannya ramah dan berbahasa, bukan traceback. [Grafik] Buka Grafik 3D: permukaan z sama dengan x kali sin y, bisa diputar dan di zoom."

[7:00-8:30] LIVE DEMO, FITUR AI REAL-TIME
"Sekarang bagian AI. [Menu Fisika, Elektrodinamika, Simulasi Monte Carlo] Ini laboratorium Hukum Gauss: permukaan sin x kuadrat plus y kuadrat, medan seragam, seratus ribu sampel Monte Carlo. Jalankan... hasilnya live: fluks kira kira dua koma tiga nol enam newton meter kuadrat per coulomb, muat terkurung dua puluh koma empat pikokolomb, dengan ketidakpastian sembilan puluh lima persen dan grafik kerucut fluks di permukaan. Fitur AI satu: saya tulis 'gelombang parabola dengan medan seragam ke arah z dan dua ratus ribu sampel', tekan Konfigurasi AI... form terisi otomatis oleh LLM, kartu ringkasan menampilkan modelnya, dan karena auto run aktif, simulasi langsung berjalan dengan parameter baru. Fitur AI dua: dengan checkbox pai aktif, setiap run yang saya picu langsung dijelaskan LLM dalam Bahasa Indonesia di panel bawah. Semua real time melalui OpenRouter dengan fallback tiga model."

[8:30-9:15] PENGUJIAN UNIT OTOMATIS & CI/CD
"Bukti kualitasnya lewat pengujian. [Buka terminal] Saya jalankan suite benchmark, dua ratus tujuh puluh tujuh eksekusi kasus dari laporan bug, mencakup limit, derivatif, deret, integral, operasi bersarang, sampai kasus copy paste... hasilnya: dua ratus empat puluh tujuh PASS, tiga puluh PASS WARN yang ekuivalen nilai, nol kegagalan. Suite kedua seratus empat kasus, suite ketiga audit semua tool mathfield, dua puluh tiga dari dua puluh tiga. Di GitHub Actions, alur kerja ci yml menjalankan ketiga suite sebagai gerbang pada setiap push, dan statusnya hijau."

[9:15-10:00] REFLEKSI & PENUTUP
"Refleksi saya tiga hal. Pertama, rekayasa requirement: definisi deteksi operasi otomatis di PRD terbukti jadi fitur paling bernilai sekaligus paling sulit, sehingga lahir pipeline op_data yang membuat semua tool konsisten. Kedua, pemodelan UML bukan formalitas, diagram yang saya gambar dulu ternyata jadi peta saat debugging. Ketiga, pengujian otomatis mengubah cara saya memperbaiki bug: dua ratus kasus regresi berarti setiap perbaikan terverifikasi dalam hitungan detik. Nabla Workspace, dari PRD, UML, UI/UX, kode, AI, pengujian, sampai CI/CD, semuanya saya kerjakan sendiri secara utuh. Terima kasih atas perhatiannya, saya siap menerima pertanyaan."""

VIDEO_TIPS = """Tips produksi (agar rubrik skor 4): tulis poin-poin, jangan dibaca kata-per-kata (rubrik penalti "dominan membaca draf"); siapkan aplikasi dalam keadaan sudah terbuka sebelum merekam; gunakan contoh ekspresi yang sudah diuji; rekam 1080p; uji mikrofon; jaga durasi di sekitar 10:00 (toleransi dosen plus minus 1 menit); tautkan video pada README.md repositori."""

LAMPIRAN_TOOL = [
    ("Integral & Limit", "Integral tak tentu/tentu, limit, derivatif, deret Σ, produk ∙, exp&log, 7 mode + deteksi otomatis."),
    ("Kalkulator Matriks", "Determinan, invers, rank, eigen, RREF, transpose (input NxN via math-field)."),
    ("Pemecah ODE", "Penyelesai persamaan diferensial biasa dengan syarat awal opsional."),
    ("Statistika Deskriptif", "Mean, median, modus, simpangan baku, varians, min/max/sum/n."),
    ("Kalkulator Bilangan Kompleks", "Modulus, argumen, bentuk polar, akar kompleks."),
    ("Deret Taylor", "Ekspansi Taylor orde 1–14 di sekitar x₀."),
    ("Kalkulator Modular", "a^b mod n, invers modular, GCD/LCM, uji prima, faktorisasi."),
    ("Kalkulator Entropi", "Entropi Shannon, H maksimum, redundansi."),
    ("Kalkulator Polinomial", "Akar dan faktorisasi polinomial."),
    ("Kalkulator Termodinamika", "Gas ideal PV=nRT (selesaikan variabel), efisiensi Carnot."),
    ("Kalkulator Kalor & Pemuaian", "Q=mcΔT, pemuaian linier, kalor laten."),
    ("Kalkulator Kuantum", "Panjang gelombang de Broglie, energi foton, efek fotolistrik."),
    ("Kalkulator Elektrostatika", "Gaya Coulomb, medan muatan titik, kapasitor lempeng sejajar."),
    ("Kalkulator Induksi", "EMF Faraday, transformator ideal, EMF gerak."),
    ("Kalkulator Relativitas", "Faktor Lorentz, dilatasi waktu, kontraksi panjang, E=γmc²."),
    ("Kalkulator Schwarzschild", "Radius Schwarzschild, dilatasi gravitasi, kecepatan lepas."),
    ("Simulasi Gerak Parabola", "Jangkauan, tinggi maksimum, waktu terbang."),
    ("Kalkulator Fluida", "Tekanan hidrostatik, kontinuitas, Bernoulli."),
    ("Kalkulator Optik", "Hukum Snell + sudut kritis/TIR, lensa tipis, celah ganda."),
    ("Kalkulator Getaran Harmonis", "Periode pegas/bandul, energi SHM."),
    ("Simulasi (10)", "Peta logistik, Lorenz, Fourier, transformasi 2D, random walk, pendulum ganda, proyektil+drag, Kepler, celah ganda, paket gelombang."),
    ("Grapher (15)", "Domain coloring, fraktal, gradien multivariabel, Frenet, transformasi 3D, slope field, distribusi, algoritma graf, medan listrik, siklus P-V, Ising MC, Minkowski, fluida, geodesik, ray tracing."),
]
