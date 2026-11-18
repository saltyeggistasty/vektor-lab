import os
import re
import sys
import json
import time
import smtplib
from email.message import EmailMessage
from flask import Flask, jsonify, render_template, request, abort, send_from_directory

import vectorcalc as vc
import physics as ph
import mathlab as ml
import simlab as sl
import graphlab as gl

# ---- mode frozen (exe PyInstaller): folder data = bundle _internal ----
FROZEN = getattr(sys, "frozen", False)

def _base():
    """Folder berisi data runtime (templates/static/i18n/menu_screen/...).
    Saat frozen: bundle _internal dari PyInstaller; saat dev: folder proyek."""
    if FROZEN:
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# folder unduhan build offline (diisi build_offline.py; hanya ada saat dev)
DOWNLOAD_DIR = os.path.join(_base(), "Nabla Workspace x64 Offline")

app = Flask(__name__)
# matikan cache statik: semua update css/js/gambar ambil versi terbaru
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# batas upload form audit (foto) — 8 MB cukup untuk foto profil
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def api(fn):
    def wrapper():
        try:
            return jsonify(ok=True, data=fn(request.get_json(force=True) or {}))
        except ml.LabError as e:
            # error terstruktur: bawa kunci i18n + args biar frontend
            # menampilkan pesan dalam bahasa aktif
            return jsonify(ok=False, error=str(e),
                           errKey=getattr(e, "key", None),
                           errArgs=list(getattr(e, "i18n_args", []) or [])), 400
        except ph.PhysError as e:
            return jsonify(ok=False, error=str(e),
                           errKey=getattr(e, "key", None),
                           errArgs=list(getattr(e, "i18n_args", []) or [])), 400
        except vc.CalcError as e:
            return jsonify(ok=False, error=str(e),
                           errKey=getattr(e, "key", None),
                           errArgs=list(getattr(e, "i18n_args", []) or [])), 400
        except (ValueError, TypeError, KeyError) as e:
            return jsonify(ok=False, error=f"Input tidak valid: {e}"), 400
    wrapper.__name__ = fn.__name__
    return wrapper


def num(v, default=0.0):
    return float(v) if v not in (None, "") else default


def point_of(d):
    p = d.get("point")
    return [num(c) for c in p] if p else None


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/calc")
@api
def calc(d):
    return vc.calculate(
        d.get("op"), f=d.get("f"), F=d.get("F"), point=point_of(d),
        order=d.get("order", 1), var=d.get("var", "x"),
        direction=d.get("direction"),
    )


@app.post("/api/surface")
@api
def surface(d):
    return vc.surface(d.get("f"), [num(d.get("xmin"), -3), num(d.get("xmax"), 3)],
                      [num(d.get("ymin"), -3), num(d.get("ymax"), 3)], d.get("n", 60))


@app.post("/api/field")
@api
def field(d):
    return vc.field(d.get("F") or [], [num(d.get("min"), -2), num(d.get("max"), 2)],
                    d.get("n", 5))


@app.post("/api/curve")
@api
def curve(d):
    return vc.curve(d.get("r") or [], [num(d.get("tmin"), 0), num(d.get("tmax"), 6.2832)],
                    d.get("n", 400))


@app.post("/api/physics/simulate")
@api
def phys_sim(d):
    return ph.phys_simulation(d)


@app.post("/api/physics/ai")
@api
def phys_ai(d):
    return ph.ai_configure(d.get("description"), d.get("current"), d.get("lang"))


@app.post("/api/physics/interpret")
@api
def phys_interpret(d):
    return ph.ai_interpret(d.get("stats") or {}, d.get("context") or {},
                           d.get("lang"))


# ---- Nabla Lab: kalkulator/simulasi tool cards baru (modul mathlab.py) ----
@app.post("/api/lab")
@api
def lab(d):
    tid = d.get("tool")
    if tid in gl.TOOLS:                     # advanced graphers (graphlab.py)
        return gl.run_tool(tid, d.get("data") or {})
    if tid in sl.TOOLS:                     # simulasi advanced (simlab.py)
        return sl.run_tool(tid, d.get("data") or {})
    return ml.run_tool(tid, d.get("data") or {})




# ---- folder loading_screen: gambar + config untuk loading screen (modular) ----
LOADER_DIR = os.path.join(_base(), "loading_screen")
LOADER_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".json"}

@app.route("/loading_screen/<path:fn>")
def loading_fn(fn):
    if os.path.splitext(fn)[1].lower() not in LOADER_EXTS:
        abort(404)
    return send_from_directory(LOADER_DIR, fn)


# ---- folder menu_screen: cover art untuk menu "Physics War Stories" ----
MENUSCREEN_DIR = os.path.join(_base(), "menu_screen")
MENUSCREEN_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

@app.route("/menu_screen/<path:fn>")
def menu_screen_fn(fn):
    if os.path.splitext(fn)[1].lower() not in MENUSCREEN_EXTS:
        abort(404)
    return send_from_directory(MENUSCREEN_DIR, fn)


# ---- folder language_select_backdrop: foto latar layar pemilih bahasa ----
LSBACKDROP_DIR = os.path.join(_base(), "language_select_backdrop")
# .mp4/.webm: video backdrop Indonesia (pengganti foto statis Elang Jawa)
LSBACKDROP_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm"}

@app.route("/language_select_backdrop/<path:fn>")
def lsbackdrop_fn(fn):
    if os.path.splitext(fn)[1].lower() not in LSBACKDROP_EXTS:
        abort(404)
    # conditional=True: dukung Range request — wajib buat <video>
    # (biar bisa streaming + seek, bukan download penuh 48MB dulu)
    return send_from_directory(LSBACKDROP_DIR, fn, conditional=True)


# ---- folder about_us_menu: foto profil tim di layar "About us" ----
ABOUT_DIR = os.path.join(_base(), "about_us_menu")
ABOUT_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

@app.route("/about_us_menu/<path:fn>")
def about_fn(fn):
    if os.path.splitext(fn)[1].lower() not in ABOUT_EXTS:
        abort(404)
    return send_from_directory(ABOUT_DIR, fn)


@app.after_request
def no_stale_assets(resp):
    # Aset GAK BOLEH STALE: CSS/JS/foto/video wajib revalidasi tiap load
    # (ETag -> 304 kalau gak berubah, jadi tetap hemat). Browser cache yang
    # suka nyangkut = musuh: CSS/JS lama bikin fitur baru keliatan "gak jalan".
    if request.path.startswith(
        ("/static/", "/menu_screen/", "/language_select_backdrop/", "/i18n/")
    ):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


# ---- cache-busting URL aset (?v=...) --------------------------------------
# ASSET_V = waktu boot server. index.html manggil url_for(..., v=asset_v),
# jadi tiap restart server URL aset berubah -> browser/SW GAK MUNGKIN
# nyimpen salinan lama. Ini pelengkap header no-cache di atas.
ASSET_V = str(int(time.time()))

@app.context_processor
def _asset_v():
    return {"asset_v": ASSET_V}


# ---- folder i18n: berkas bahasa (english.json dll) untuk pemilih bahasa ----
I18N_DIR = os.path.join(_base(), "i18n")

@app.route("/i18n/<path:fn>")
def i18n_fn(fn):
    if os.path.splitext(fn)[1].lower() != ".json":
        abort(404)
    return send_from_directory(I18N_DIR, fn)


# ---- address.json: alamat wallet donasi (bisa diedit manual pemilik web) ----
ADDRESS_FILE = os.path.join(_base(), "address.json")

@app.route("/donation_addresses")
def donation_addresses():
    with open(ADDRESS_FILE, encoding="utf-8") as f:
        return jsonify(json.load(f))


# ---- form audit donasi: kirim isian + foto publik ke email pemilik web ----
# kredensial SMTP dibaca FRESH tiap request dari config.json (blok audit_email),
# jadi pemilik bisa ganti password/alamat tanpa restart server.
CONFIG_FILE = os.path.join(_base(), "config.json")

AUDIT_PHOTO_EXT = {".png", ".jpg", ".jpeg", ".webp"}

def _audit_cfg():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        cfg = json.load(f).get("audit_email") or {}
    for k in ("to", "user", "app_password"):
        if not cfg.get(k):
            raise ValueError(f"config.json: audit_email.{k} belum diisi")
    return cfg

def _clean(v, maxlen=300):
    return re.sub(r"[\r\n\t]+", " ", str(v or "").strip())[:maxlen]

@app.post("/api/audit")
def audit_form():
    try:
        cfg = _audit_cfg()
    except Exception as e:
        return jsonify(ok=False, error=f"Konfigurasi email audit belum siap: {e}"), 500

    fullname = _clean(request.form.get("fullname"))
    nickname = _clean(request.form.get("nickname"))
    country = _clean(request.form.get("country"))
    humanitarian = _clean(request.form.get("humanitarian"), 2000)
    orgstatus = _clean(request.form.get("orgstatus"), 300)
    public = "ya" if request.form.get("public") == "ya" else "tidak"

    # wajib: nama lengkap, panggilan, asal negara, dan foto publik
    if not fullname or not nickname or not country:
        return jsonify(ok=False, error="Nama lengkap, nama panggilan, dan asal negara wajib diisi."), 400
    photo = request.files.get("photo")
    if not photo or not photo.filename:
        return jsonify(ok=False, error="Foto publik wajib diunggah."), 400
    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in AUDIT_PHOTO_EXT:
        return jsonify(ok=False, error="Foto harus PNG/JPG/WEBP."), 400
    data = photo.read()
    if not data:
        return jsonify(ok=False, error="Foto kosong / gagal dibaca."), 400

    body = (
        "Form Audit Donasi Baru\n"
        "=======================\n\n"
        f"Nama Lengkap      : {fullname}\n"
        f"Nama Akrab/Panggilan: {nickname}\n"
        f"Asal Negara       : {country}\n"
        f"Pengalaman Kemanusiaan (opsional): {humanitarian or '-'}\n"
        f"Univ/Kota/Status/Pekerjaan (opsional): {orgstatus or '-'}\n"
        f"Ikut Audit Publik/Sosial: {public}\n"
    )

    mime = {".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".webp": "image/webp"}[ext]
    msg = EmailMessage()
    msg["From"] = cfg["user"]
    msg["To"] = cfg["to"]
    msg["Subject"] = f"[Audit Donasi] {fullname} — {country}"
    msg.set_content(body)
    msg.add_attachment(data, maintype=mime.split("/")[0], subtype=mime.split("/")[1],
                       filename=f"audit_photo{ext}")

    try:
        with smtplib.SMTP(cfg.get("smtp_host", "smtp.gmail.com"),
                          int(cfg.get("smtp_port", 587)), timeout=30) as s:
            s.starttls()
            s.login(cfg["user"], cfg["app_password"].replace(" ", ""))
            s.send_message(msg)
    except Exception as e:
        return jsonify(ok=False, error=f"Gagal mengirim email: {e}"), 502
    return jsonify(ok=True, data={"sent": True})


@app.post("/api/feedback")
def feedback_form():
    """Form kritik/saran/lapor bug dari layar About us.
    Kirim ke email pemilik web (SMTP config sama dengan audit) —
    TANPA foto & tanpa field wajib identitas, cukup pesan."""
    try:
        cfg = _audit_cfg()
    except Exception as e:
        return jsonify(ok=False, error=f"Konfigurasi email belum siap: {e}"), 500

    name = _clean(request.form.get("name"), 200)
    contact = _clean(request.form.get("contact"), 200)
    kind = request.form.get("kind", "saran")
    kind = kind if kind in ("bug", "saran") else "saran"
    message = re.sub(r"[ \t]+", " ", str(request.form.get("message") or "").strip())[:5000]

    if not message:
        return jsonify(ok=False, error="Pesan nya jangan kosong ya."), 400

    label = "LAPOR BUG" if kind == "bug" else "KRITIK/SARAN"
    body = (
        f"Form {label} Baru — Layar About us\n"
        "====================================\n\n"
        f"Nama    : {name or '-'}\n"
        f"Kontak  : {contact or '-'}\n"
        f"Jenis   : {label}\n\n"
        "Pesan:\n"
        f"{message}\n"
    )

    msg = EmailMessage()
    msg["From"] = cfg["user"]
    msg["To"] = cfg["to"]
    reply = contact if ("@" in contact or contact.replace(" ", "").startswith("+")) else ""
    msg["Subject"] = f"[About us - {label}] {name or 'Anonim'}"
    msg.set_content(body)
    if reply:
        msg["Reply-To"] = reply

    try:
        with smtplib.SMTP(cfg.get("smtp_host", "smtp.gmail.com"),
                          int(cfg.get("smtp_port", 587)), timeout=30) as s:
            s.starttls()
            s.login(cfg["user"], cfg["app_password"].replace(" ", ""))
            s.send_message(msg)
    except Exception as e:
        return jsonify(ok=False, error=f"Gagal mengirim email: {e}"), 502
    return jsonify(ok=True, data={"sent": True})


# ---- info aplikasi: frontend tahu dia jalan di exe offline atau web ----
@app.get("/api/appinfo")
def appinfo():
    return jsonify(ok=True, data={"frozen": FROZEN})


# ---- unduhan build offline (zip dibuat build_offline.py) ----
# Hanya aktif saat dev (web): di exe frozen folder ini tidak disertakan.
_DL_CACHE = {"mtime": None, "info": None}

def _dl_info():
    # cache per-mtime: sha256 zip 236MB itu 1-2+ detik di HDD — kalau
    # dihitung ulang tiap request, panel download nunggu lama & rawan
    # gagal sementara (teks merah kedip). Rebuild = mtime berubah = hitung ulang.
    fn = "NablaWorkspace-x64.zip"
    p = os.path.join(DOWNLOAD_DIR, fn)
    if not os.path.exists(p):
        return None
    mtime = int(os.path.getmtime(p))
    if _DL_CACHE["mtime"] == mtime and _DL_CACHE["info"]:
        return _DL_CACHE["info"]
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    info = {"file": fn, "size": os.path.getsize(p),
            "sha256": h.hexdigest(), "mtime": mtime}
    _DL_CACHE["mtime"] = mtime
    _DL_CACHE["info"] = info
    return info

@app.get("/download/info")
def download_info():
    return jsonify(ok=True, data=_dl_info())

@app.get("/download/offline")
def download_offline():
    info = _dl_info()
    if not info:
        abort(404)
    return send_from_directory(DOWNLOAD_DIR, info["file"], as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
