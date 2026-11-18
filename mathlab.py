# ============================================================
# NABLA LAB - mesin kalkulator/simulasi generik untuk tool cards baru.
# MODUL TERPISAH: GAK nyentuh physics.py / vectorcalc.py sama sekali.
# Semua tool balikin dict polos (rows/latex/plot) - frontend (tools.js)
# yang ngurusi label i18n & render. Error user = raise LabError.
# Catatan: label row dipakai sebagai KUNCI oleh tools.js (ASCII aja),
# bukan buat ditampilan langsung - terjemahan ada di JSON i18n.
# ============================================================
import math
import re

import numpy as np
import sympy as sp

X = sp.Symbol("x")


class LabError(ValueError):
    """Error input/tool yang aman ditampilkan ke user.
    key + args opsional: kunci i18n & argumen biar frontend bisa
    menerjemahkan pesan ke bahasa aktif (fallback = msg Indonesia)."""

    def __init__(self, msg, key=None, *args):
        super().__init__(msg)
        self.key = key
        self.i18n_args = list(args)


def _num(v, name, minv=None, maxv=None, allow_zero=True):
    """Parse float ketat: wajib angka berhingga."""
    try:
        f = float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        raise LabError(f"Nilai '{name}' bukan angka yang valid.",
                       "err.not_number", name)
    if not math.isfinite(f):
        raise LabError(f"Nilai '{name}' harus angka berhingga.",
                       "err.not_finite", name)
    if not allow_zero and f == 0:
        raise LabError(f"Nilai '{name}' tidak boleh nol.",
                       "err.not_zero_allowed", name)
    if minv is not None and f < minv:
        raise LabError(f"Nilai '{name}' harus >= {minv}.",
                       "err.min", name, minv)
    if maxv is not None and f > maxv:
        raise LabError(f"Nilai '{name}' harus <= {maxv}.",
                       "err.max", name, maxv)
    return f


def _fmt(v, sig=6):
    """Angka ringkas utk ditampilkan."""
    try:
        f = float(v)
        if not math.isfinite(f):
            return str(v)
        return f"{f:.{sig}g}"
    except (TypeError, ValueError):
        return str(v)


def _expr(s, symbols=("x",), assume_int=()):
    """Parse ekspresi user jadi sympy. Symbols dibatasi biar aman.
    assume_int = nama simbol yang dibuat dgn asumsi integer+positif
    (index Σ/∏ — biar Piecewise gak muncul di hasil)."""
    s = str(s or "").strip()
    if not s:
        raise LabError("Ekspresi kosong.", "err.expr_empty")
    if len(s) > 300:
        raise LabError("Ekspresi terlalu panjang.", "err.expr_long")
    if any(w in s for w in ("__", "import", "exec", "eval", "lambda", "system")):
        raise LabError("Ekspresi mengandung kata yang tidak diizinkan.",
                       "err.expr_forbidden")
    ai = set(assume_int)
    loc = {name: (sp.Symbol(name, integer=True, positive=True)
                  if name in ai else sp.Symbol(name))
           for name in symbols}
    try:
        e = sp.sympify(s, locals=loc, rational=True)
    except Exception as e:
        raise LabError(f"Ekspresi tidak bisa dipahami: {e}", "err.expr_parse", str(e))
    if isinstance(e, sp.Expr):
        bad = [sym for sym in e.free_symbols if sym.name not in symbols]
        if bad:
            raise LabError(f"Simbol tidak dikenal: {', '.join(sorted(str(b) for b in bad))}",
                           "err.unknown_symbols",
                           ", ".join(sorted(str(b) for b in bad)))
    return e


# ---------- konstanta fisika (CODATA) ----------
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
Q_E = 1.602176634e-19
K_COULOMB = 8.9875517923e9
EPS0 = 8.8541878128e-12
R_GAS = 8.314462618
G_EARTH = 9.80665


# ============================================================
# TOOL: integral & limit
# ============================================================
# Whitelist simbol luas untuk tool integral: operator di input boleh
# pakai variabel apa pun (\int t dt, \sum_{i=1}^{4} i, batas simbolik
# \int_a^b). Nilai konstanta (pi, E, I) tetap dari sympify, gak masuk
# whitelist.
# catatan: "d" SENGAJA gak ada di whitelist — d cuma muncul di notasi
# operator (\frac{d}{dx}, dx) yang harusnya sudah dikonsumsi frontend;
# kalau bocor, jadi "Simbol tidak dikenal: d" (terlihat), bukan diam-diam
# dianggap variabel (FAIL-SILENT). "f" juga gak ada: f = nama fungsi
# (f(x) dr template turunan) — kalau jadi simbol, f(x) gak bisa dipanggil.
_INTEG_LETTERS = "xyztuvsrwnmkpqabcghjilo"
_INT_GREEK = ("theta", "alpha", "beta", "gamma", "mu", "lambda", "omega",
              "phi", "varphi", "sigma", "delta", "eta", "rho", "epsilon",
              "tau")
_INTEG_SYMS = tuple(_INTEG_LETTERS) + _INT_GREEK

# sentinel dari frontend (tools.js calculus2sympy) utk notasi yang gak
# bisa dikonversi -> pesan bersih, bukan crash / parse error mentah
_INT_SENTINELS = {
    "int_missing_dx": "Notasi integral butuh diferensial d<var>, "
                      "contoh: \\int x dx.",
    "int_unsupported": "Bentuk \\iint, \\iiint, atau \\oint belum "
                       "didukung.",
}


def _apply_op_once(expr, d, mode):
    """Operator kalkulus di input (Integral/Sum/Limit/Derivative/Product
    tak-evaluasi dari frontend) diterapkan PERSIS SEKALI.

    Aturan anti dobel-apply: operator di input MENANG. Mode dipakai cuma
    buat melengkapi info yang gak ada di notasi (mis. batas a,b dari
    field buat \\int tanpa batas, titik evaluasi buat turunan) — gak
    pernah mengulang operasi yang sudah ada di input."""
    rows = []

    def det(label):
        rows.append(["det", label, False])

    def numrow(res):
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])

    if isinstance(expr, sp.Integral):
        lims = expr.limits
        definite = all(len(l) == 3 for l in lims)
        var = lims[0][0]
        if definite:
            det("∫ definite")
            try:
                res = expr.doit()
            except Exception as e:
                raise LabError(f"Integral ini gak bisa dihitung: {e}",
                               "err.op_fail", str(e)[:120])
        else:
            if mode == "def":
                # batas dr field (mode melengkapi, bukan mengulang)
                a = _num(d.get("a"), "a")
                b = _num(d.get("b"), "b")
                det("∫ definite (batas dari field)")
                res = sp.integrate(expr.function, (var, a, b))
            else:
                det("∫ indefinite")
                res = sp.integrate(expr.function, var)
                rows.append(["sym", sp.latex(res) + " + C", True])
                numrow(res)
                return {"rows": rows, "plain": str(res) + " + C"}
        rows.append(["sym", sp.latex(res), True])
        numrow(res)
        return {"rows": rows, "plain": str(res)}

    if isinstance(expr, sp.Derivative):
        det("d/dx")
        try:
            res = expr.doit()
        except Exception as e:
            raise LabError(f"Turunan ini gak bisa dihitung: {e}",
                           "err.op_fail", str(e)[:120])
        rows.append(["dxn", sp.latex(res), True])
        xo = str(d.get("xo") or "").strip()
        if mode == "diff" and xo:
            xv = _num(xo, "x0")
            v = expr.variables[0][0] if expr.variables else X
            try:
                rows.append(["dval", _fmt(sp.N(res.subs(v, xv), 12)), False])
            except Exception:
                pass
        return {"rows": rows, "plain": str(res)}

    if isinstance(expr, sp.Limit):
        det("lim")
        try:
            res = expr.doit()
        except Exception as e:
            raise LabError(f"Limit ini gak bisa dihitung: {e}",
                           "err.op_fail", str(e)[:120])
        rows.append(["sym", sp.latex(res), True])
        numrow(res)
        return {"rows": rows, "plain": str(res)}

    if isinstance(expr, (sp.Sum, sp.Product)):
        det("Σ" if isinstance(expr, sp.Sum) else "∏")
        try:
            res = expr.doit()
            res = sp.simplify(res)
        except Exception as e:
            raise LabError(f"Deret ini gak bisa dihitung: {e}",
                           "err.op_fail", str(e)[:120])
        rows.append(["sumv", sp.latex(res), True])
        numrow(res)
        return {"rows": rows, "plain": str(res)}

    raise LabError("Operasi tidak dikenal.", "err.mode", "integral")


def _pretty_latex(e):
    """LaTeX tampilan: ln (bukan log), arcsin-style (bukan asin/atan),
    Abs -> |x|. Aturan format output (bug_reports2.md section 11)."""
    try:
        L = sp.latex(e, ln_notation=True, inv_trig_style="full")
    except TypeError:
        L = sp.latex(e)
    return (L.replace("\\lvert", "|").replace("\\rvert", "|")
             .replace("\\left\\lvert", "\\left|").replace("\\right\\rvert", "\\right|")
             .replace("\\operatorname{Abs}", "\\left|")
             .replace("\\log", "\\ln"))


def _abs_log(e):
    """∫ 1/x -> ln|x| : bungkus log(arg) dgn Abs kecuali arg terbukti
    positif (mis. x^2+1)."""
    def _wrap(u):
        try:
            if u.is_positive is True:
                return sp.log(u)
        except Exception:
            pass
        return sp.log(sp.Abs(u))
    try:
        return e.replace(sp.log, _wrap)
    except Exception:
        return e


def _best_form(e):
    """Pilih bentuk paling ringkas dari kandidat equivalent
    (bug_reports2.md 11.2: jangan simplify buta)."""
    cands = [e]
    for f in (sp.factor, sp.together, sp.cancel, sp.trigsimp, sp.radsimp,
              sp.simplify, sp.expand):
        try:
            cands.append(f(e))
        except Exception:
            pass
    try:
        return min(cands, key=lambda c: (sp.count_ops(c), len(str(c))))
    except Exception:
        return e


def _expr_int(s, assume_int=()):
    """_expr + retry perkalian implisit antar huruf ("xy" -> x*y) +
    simbol bersubskrip dari template MathLive ("x_i" -> simbol sah)."""
    s = str(s or "")
    # safety net: marker internal frontend GAK BOLEH sampai ke sympify
    # (bocor = error "forbidden words" yang membingungkan)
    if s.startswith("__NABLA_"):
        raise LabError("Notasi tidak terbaca utuh — coba tulis ulang "
                       "rumusnya.", "err.expr_parse", "marker")
    try:
        e = _expr(s, _INTEG_SYMS, assume_int=assume_int)
        # simbol gabungan multi-huruf ("ij", "xy") yang bukan greek →
        # pecah jadi perkalian implisit (nested sums S19/S20)
        bad2 = [sym.name for sym in e.free_symbols
                if len(sym.name) > 1 and sym.name not in _INT_GREEK
                and all(ch in _INTEG_LETTERS for ch in sym.name)]
        if bad2:
            s1 = s
            for nm in bad2:
                s1 = re.sub(r"(?<![A-Za-z_])" + nm + r"(?![A-Za-z_])",
                            "*".join(nm), s1)
            return _expr(s1, _INTEG_SYMS, assume_int=assume_int)
        return e
    except LabError as perr:
        names = [a.strip() for a in (perr.i18n_args[0]
                 if perr.i18n_args else "").split(",") if a.strip()]
        # 1) simbol bersubskrip (x_i, a_1): daftarkan sebagai simbol sah
        if names and all(re.fullmatch(r"[A-Za-z]_[A-Za-z0-9]+", nm)
                         for nm in names):
            return _expr(s, _INTEG_SYMS + tuple(names))
        # 2) fallback parse_expr dgn implicit multiplication +
        #    function_exponentiation (tangani bentuk sisa konversi,
        #    mis. fn powers yang lolos normalizer)
        try:
            from sympy.parsing.sympy_parser import (
                parse_expr, standard_transformations,
                implicit_multiplication_application, function_exponentiation,
                convert_xor)
            tr = standard_transformations + (
                implicit_multiplication_application(),
                function_exponentiation(), convert_xor())
            loc = {name: (sp.Symbol(name, integer=True, positive=True)
                          if name in assume_int else sp.Symbol(name))
                   for name in _INTEG_SYMS}
            for nm in names:
                loc[nm] = sp.Symbol(nm)
            e = parse_expr(s, local_dict=loc, transformations=tr)
            if isinstance(e, sp.Expr):
                bad = [sym for sym in e.free_symbols
                       if sym.name not in _INTEG_SYMS and
                       sym.name not in loc and
                       not re.fullmatch(r"[A-Za-z]_[A-Za-z0-9]+", sym.name)]
                if not bad:
                    # guard: fungsi TAK teraplikasi (sin tanpa argumen)
                    # jangan dibiarkan dihitung (K1: FunctionClass ** int)
                    unapplied = [nd for nd in sp.preorder_traversal(e)
                                 if isinstance(nd, type) and
                                 issubclass(nd, sp.Expr)]
                    if unapplied:
                        raise LabError(
                            "Fungsi '" + ", ".join(
                                str(u.__name__ if hasattr(u, "__name__")
                                    else u) for u in unapplied) +
                            "' butuh argumen — tulis mis. sin(x).",
                            "err.fn_no_arg",
                            ", ".join(str(u) for u in unapplied))
                    return e
        except LabError:
            raise
        except Exception:
            pass
        # 3) perkalian implisit antar huruf ("xy" -> x*y)
        splittable = bool(names) and all(
            len(nm) > 1 and nm not in _INT_GREEK and
            all(ch in _INTEG_LETTERS for ch in nm)
            for nm in names)
        if not splittable:
            raise
        s1 = str(s)
        for nm in names:
            s1 = re.sub(r"(?<![A-Za-z_])" + nm + r"(?![A-Za-z_])",
                        "*".join(nm), s1)
        return _expr(s1, _INTEG_SYMS, assume_int=assume_int)


def _bound(v, assume_int=()):
    """Batas/titik dr op_data: angka, simbol, oo. Gagal parse = pesan
    bersih 'tidak valid' (bukan sympify dump) — kejadian pas user baru
    ngisi setengah notasi di mathfield."""
    try:
        return _expr_int(str(v), assume_int=assume_int)
    except LabError:
        raise LabError(f"Nilai batas/titik '{v}' tidak valid — isi angka, "
                       "simbol, atau oo.", "err.bound_invalid", str(v)[:40])


def _build_op(opd, int_syms=()):
    """Bangun objek sympy UNEVALUATED dari op_data terstruktur (JSON dr
    frontend). Body = plain sympy string ATAU opd bersarang (mis. Subs
    di dalam turunan). Dibangun programatik -> sympify gak pernah
    mengevaluasi operator di muka (Derivative auto-eval = fitur orde/
    titik evaluasi bisa rusak). int_syms = index var Σ/∏ yang dapat
    asumsi integer+positif (biar inner Integral gak ngeluarin Piecewise)."""
    t = opd.get("op")
    if t == "eval":
        return _expr_int(str(opd.get("body") or ""), assume_int=int_syms)
    # index var Σ/∏: simbol BERASUMSI (integer+positif) — konsisten dgn
    # body parse & dummy Sum/Prod (biar nested Integral gak Piecewise)
    v = sp.Symbol(str(opd.get("var") or "x"), integer=True, positive=True) \
        if t in ("sum", "product") else sp.Symbol(str(opd.get("var") or "x"))
    if t == "subs_deriv":
        # GAK punya "body" — inner opd dibangun rekursif
        inner = _build_op(opd.get("sub") or {"op": "eval", "body": ""},
                          int_syms=int_syms)
        return sp.Subs(inner, v, _bound(opd.get("point") or "0", int_syms))
    raw = opd.get("body")
    # index var Σ/∏ ikut dgn asumsi utk parse body (nested C05 dsb)
    body_int = int_syms + ((str(opd.get("var") or "x"),)
                           if t in ("sum", "product") else ())
    body = _build_op(raw, int_syms=body_int) if isinstance(raw, dict) \
        else _expr_int(str(raw or ""), assume_int=body_int)
    if t == "integral":
        if opd.get("has_bounds"):
            return sp.Integral(body, (v, _bound(opd["a"], int_syms),
                                      _bound(opd["b"], int_syms)))
        return sp.Integral(body, v)
    if t == "derivative":
        if opd.get("vars"):
            # multi-var (\partial x \partial y): [(var, orde), ...]
            return sp.Derivative(body, *[
                (sp.Symbol(nm), int(o or 1)) for nm, o in opd["vars"]])
        return sp.Derivative(body, (v, int(opd.get("order") or 1)))
    if t == "limit":
        at = _bound(opd.get("at") or "0", int_syms)
        return sp.Limit(body, v, at, dir=str(opd.get("dir") or "+"))
    if t == "sum":
        return sp.Sum(body, (v, _bound(opd["a"], int_syms),
                             _bound(opd["b"], int_syms)))
    if t == "product":
        return sp.Product(body, (v, _bound(opd["a"], int_syms),
                                 _bound(opd["b"], int_syms)))
    raise LabError("Operasi tidak dikenal.", "err.mode", "integral")


def _apply_opd(opd, d, mode):
    """Jalankan operator kalkulus dari op_data PERSIS SEKALI.
    Mode cuma melengkapi (batas field utk integral tanpa batas, titik
    evaluasi utk turunan) — GAK pernah mengulang operasi di input."""
    rows = []

    def det(label):
        rows.append(["det", label, False])

    def numrow(res):
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])

    try:
        expr = _build_op(opd)
    except LabError:
        raise
    except Exception as e:
        raise LabError(f"Notasi operator gak bisa dipahami: {e}",
                       "err.expr_parse", str(e)[:120])

    def finish(res, add_c=False):
        if opd.get("extra"):
            try:
                ex = opd["extra"]
                res = res + (_build_op(ex) if isinstance(ex, dict)
                             else _expr_int(str(ex)))
            except LabError:
                pass
        return res

    if isinstance(expr, sp.Integral):
        lims = expr.limits
        definite = all(len(l) == 3 for l in lims)
        var = lims[0][0]
        if definite:
            det("∫ definite")
            res = expr.doit()
        elif mode == "def":
            a = _num(d.get("a"), "a")
            b = _num(d.get("b"), "b")
            det("∫ definite (batas dari field)")
            res = sp.integrate(expr.function, (var, a, b))
        else:
            det("∫ indefinite")
            res = sp.integrate(expr.function, var)
            res = finish(res)
            resf = _abs_log(_best_form(res))
            rows.append(["sym", _pretty_latex(resf) + " + C", True])
            numrow(res)
            return {"rows": rows, "plain": str(resf) + " + C"}
        res = finish(res)
        resf = _best_form(res)
        rows.append(["sym", _pretty_latex(resf), True])
        numrow(res)
        return {"rows": rows, "plain": str(resf)}

    if isinstance(expr, sp.Derivative):
        det("d/dx")
        # mode diff MANUAL: field "Derivative order n" kalo diisi = OVERRIDE
        # orde dr editor (\frac{d}{dx} x^3 + n=6 -> d^6/dx^6 x^3). Mode auto:
        # orde editor yang dipakai. Field n gak punya default -> aman
        # (kosong = gak pernah nge-override).
        v = sp.Symbol(str(opd.get("var") or "x"))
        if (mode == "diff" and opd.get("var") and
                str(d.get("n") or "").strip()):
            nf = int(_num(d["n"], "n"))
            if nf < 1 or nf > 12:
                raise LabError("Orde turunan n harus antara 1 sampai 12.",
                               "err.between", "n", 1, 12)
            body = expr.expr
            expr = sp.Derivative(body, (v, nf))
        res = expr.doit()
        resf = _best_form(res)
        # titik evaluasi x (opsional, field xo) -> baris nilai di titik itu
        if str(d.get("xo") or "").strip():
            xv = _bound(d["xo"])
            res = finish(res)
            rows.append(["dxn", _pretty_latex(resf), True])
            try:
                rows.append(["dval", _fmt(sp.N(resf.subs(v, xv), 12)), False])
            except Exception:
                pass
            return {"rows": rows, "plain": str(resf)}
        res = finish(res)
        rows.append(["dxn", _pretty_latex(resf), True])
        return {"rows": rows, "plain": str(resf)}

    if isinstance(expr, sp.Limit):
        det("lim")
        # mode lim MANUAL: field "Titik didekati x0" kalo diisi = OVERRIDE
        # titik dr editor (x0 gak punya default -> aman)
        if mode == "lim" and str(d.get("x0") or "").strip():
            xv = _bound(d["x0"])
            v = sp.Symbol(str(opd.get("var") or "x"))
            expr = sp.Limit(expr.args[0], v, xv)
        # nested operator di body (Integral/Sum) di-evaluate DULU,
        # baru limitnya dihitung (L21-L23, C07)
        # Limit.args = (fungsi, var, titik, arah) — datar
        nested = isinstance(opd.get("body"), dict)
        fn_done = expr.args[0].doit()
        atv = expr.args[2]
        dirv = str(expr.args[3]) if len(expr.args) > 3 else "+"
        if nested and atv != oo:
            # sympy limit sering gagal utk nested Integral/Sum (erfi/
            # fresnel — L22/L23/C07) → fallback ekspansi seri di titik
            # limit, lalu ambil nilai di titiknya
            try:
                ser = fn_done.series(expr.args[1], atv, 8).removeO()
                res = ser.subs(expr.args[1], atv)
            except Exception:
                res = sp.Limit(fn_done, expr.args[1], atv, dir=dirv).doit()
        else:
            res = sp.Limit(fn_done, expr.args[1], atv, dir=dirv).doit()
        res = finish(res)
        resf = _best_form(res)
        rows.append(["sym", _pretty_latex(resf), True])
        numrow(res)
        return {"rows": rows, "plain": str(resf)}

    if isinstance(expr, (sp.Sum, sp.Product)):
        is_prod = isinstance(expr, sp.Product)
        det("∏" if is_prod else "Σ")
        res = expr.doit()
        res = sp.simplify(res)
        res = finish(res)
        resf = _best_form(res)
        rows.append(["prodv" if is_prod else "sumv", _pretty_latex(resf), True])
        numrow(res)
        return {"rows": rows, "plain": str(resf)}

    if isinstance(expr, sp.Subs):
        # bar evaluasi \left.\frac{d}{dx} f\right|_{x=a}
        det("d/dx | x=a")
        res = expr.doit()
        res = finish(res)
        resf = _best_form(res)
        if resf.free_symbols:
            rows.append(["sym", _pretty_latex(resf), True])
        else:
            rows.append(["dval", _fmt(sp.N(resf, 12)), False])
        return {"rows": rows, "plain": str(resf)}

    raise LabError("Operasi tidak dikenal.", "err.mode", "integral")


def tool_integral(d):
    es = str(d.get("expr") or "").strip()
    # sentinel notasi rusak dari frontend -> pesan bersih
    if es.startswith("__NABLA_ERR__:"):
        key = es.split(":", 1)[1].strip() or "int_unsupported"
        raise LabError(_INT_SENTINELS.get(key, "Notasi tidak didukung."),
                       "err." + key)

    # jalur UTAMA: op_data terstruktur dari frontend (anti dobel-apply
    # & anti sympify auto-eval)
    opd = d.get("op_data")
    if isinstance(opd, dict) and opd.get("op"):
        return _apply_opd(opd, d, d.get("mode", "def"))

    expr = _expr_int(es)
    mode = d.get("mode", "def")

    # operator kalkulus di input (Integral/Sum/Limit/Derivative/Product
    # tak-evaluasi) -> terapkan SEKALI, mode gak mengulangnya
    if isinstance(expr, (sp.Integral, sp.Derivative, sp.Limit,
                         sp.Sum, sp.Product)):
        return _apply_op_once(expr, d, mode)

    if mode == "auto":
        # ekspresi polos tanpa operator: evaluasi/sederhanakan saja
        resf = _best_form(res := sp.simplify(expr))
        rows = [["sym", _pretty_latex(resf), True]]
        if not resf.free_symbols:
            rows.append(["num", _fmt(sp.N(resf, 12)), False])
        return {"rows": rows, "plain": str(resf)}
    if mode == "def":
        a = _num(d.get("a"), "a")
        b = _num(d.get("b"), "b")
        res = sp.integrate(expr, (X, a, b))
        rows = [["sym", _pretty_latex(_best_form(res)), True]]
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])
        return {"rows": rows, "plain": str(res)}
    if mode == "indef":
        res = sp.integrate(expr, X)
        resf = _abs_log(_best_form(res))
        return {"rows": [["sym", _pretty_latex(resf) + " + C", True]], "plain": str(resf) + " + C"}
    if mode == "lim":
        x0 = _num(d.get("x0"), "x0")
        res = sp.limit(expr, X, x0)
        resf = _best_form(res)
        rows = [["sym", _pretty_latex(resf), True]]
        if not resf.free_symbols:
            rows.append(["num", _fmt(sp.N(resf, 12)), False])
        return {"rows": rows, "plain": str(resf)}
    if mode == "diff":
        # turunan ke-n, bisa dievaluasi di titik opsional x0
        n = int(_num(d.get("n") or 1, "n"))
        if n < 1 or n > 12:
            raise LabError("Orde turunan n harus antara 1 sampai 12.",
                   "err.between", "n", 1, 12)
        res = sp.diff(expr, X, n)
        rows = [["dxn", sp.latex(res), True]]
        xo = str(d.get("xo") or "").strip()
        if xo:
            xv = _num(xo, "x0")
            val = res.subs(X, xv)
            rows.append(["dval", _fmt(sp.N(val, 12)), False])
        return {"rows": rows, "plain": str(res)}
    if mode == "sum":
        # jumlah berhingga Σ f(x), a..b; usahakan bentuk simbolik dulu
        a = int(_num(d.get("a"), "a"))
        b = int(_num(d.get("b"), "b"))
        if b - a > 100000:
            raise LabError("Rentang jumlah terlalu besar (maks 100000 suku).",
                   "err.sum_range", "100000")
        try:
            res = sp.summation(expr, (X, a, b))
            res = sp.simplify(res)
        except Exception:
            res = sum(expr.subs(X, k) for k in range(a, b + 1))
            res = sp.simplify(res)
        rows = [["sumv", _pretty_latex(_best_form(res)), True]]
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])
        return {"rows": rows, "plain": str(res)}
    if mode == "prod":
        # perkalian berhingga ∏ f(x), a..b
        a = int(_num(d.get("a"), "a"))
        b = int(_num(d.get("b"), "b"))
        if b - a > 100000:
            raise LabError("Rentang perkalian terlalu besar (maks 100000 faktor).",
                   "err.sum_range", "100000")
        try:
            res = sp.product(expr, (X, a, b))
            res = sp.simplify(res)
        except Exception:
            res = sp.prod([expr.subs(X, k) for k in range(a, b + 1)])
            res = sp.simplify(res)
        rows = [["prodv", sp.latex(res), True]]
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])
        return {"rows": rows, "plain": str(res)}
    if mode == "exp":
        # eksponensial & logaritma: sederhanakan paksa bentuk e/ln
        res = sp.simplify(sp.powsimp(sp.expand_log(
            expr.rewrite(sp.exp).doit(), force=False)))
        rows = [["sym", _pretty_latex(_best_form(res)), True]]
        if not res.free_symbols:
            rows.append(["num", _fmt(sp.N(res, 12)), False])
        return {"rows": rows, "plain": str(res)}
    raise LabError("Mode integral tidak dikenal.", "err.mode", "integral")


# ============================================================
# TOOL: kalkulator matriks
# ============================================================
def _matrix_cell(c):
    r"""Sel matriks dr editor LaTeX: angka / ekspresi aritmetika sederhana
    (\frac, \pi, ^, \cdot). Simbol huruf = ditolak dengan pesan jelas."""
    c = str(c or "").strip()
    if not c:
        raise LabError("Ada sel matriks yang kosong.", "err.matrix_cell_empty")
    c = c.replace("\\cdot", "*").replace("\\times", "*").replace("\\div", "/")
    c = c.replace("\\left", "").replace("\\right", "")
    c = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", c)
    c = c.replace("\\pi", "pi").replace("^", "**")
    c = re.sub(r"\\[a-zA-Z]+", "", c)   # makro lain sisa -> dibuang
    if re.search(r"[A-Za-df-z]", c.replace("pi", "")):  # sisa huruf = simbol
        # 'e' dibiarin (Euler); huruf lain bukan angka
        raise LabError(f"Sel matriks '{c}' harus berupa angka.",
                       "err.matrix_cell_num", c)
    try:
        v = sp.sympify(c, rational=True, locals={"pi": sp.pi})
    except Exception:
        raise LabError(f"Sel matriks '{c}' tidak valid.",
                       "err.matrix_cell_num", c)
    if not v.is_number:
        raise LabError(f"Sel matriks '{c}' harus berupa angka.",
                       "err.matrix_cell_num", c)
    return v


def _parse_matrix(s):
    s = str(s or "").strip()
    if not s:
        raise LabError("Matriks kosong.", "err.matrix_empty")
    # LaTeX pmatrix/bmatrix/vmatrix/Bmatrix dr mathfield (Insert matrix
    # NxN apa pun) — baris dipisah \\, sel dipisah &
    m = re.search(r"\\begin\{([pbvB]matrix)\}([\s\S]*?)\\end\{\1\}", s)
    if m:
        rows = []
        for rline in re.split(r"\\\\|;", m.group(2)):
            rline = rline.strip()
            if not rline:
                continue
            cells = [_matrix_cell(c) for c in rline.split("&")
                     if c.strip() != ""]
            if cells:
                rows.append(cells)
    else:
        rows = []
        for rline in s.split(";"):
            rline = rline.strip()
            if not rline:
                continue
            cells = []
            for cell in re.split(r"[,\s]+", rline):
                if cell == "":
                    continue
                if re.fullmatch(r"-?\d+", cell):
                    cells.append(sp.Rational(cell))
                else:
                    cells.append(_num(cell, "matriks"))
            if cells:
                rows.append(cells)
    if not rows:
        raise LabError("Matriks kosong.", "err.matrix_empty")
    w = len(rows[0])
    if any(len(r) != w for r in rows):
        raise LabError("Semua baris harus punya jumlah kolom yang sama.",
                   "err.matrix_rows")
    return sp.Matrix(rows)


def tool_matrix(d):
    M = _parse_matrix(d.get("matrix"))
    op = d.get("op", "det")
    out = {"matrix_in": sp.latex(M)}
    if op == "det":
        if not M.is_square:
            raise LabError("Determinan hanya untuk matriks persegi.",
                   "err.matrix_square")
        out["rows"] = [["R", sp.latex(M.det()), True]]
    elif op == "inv":
        if not M.is_square:
            raise LabError("Invers hanya untuk matriks persegi.",
                   "err.matrix_square")
        try:
            out["rows"] = [["R", sp.latex(M.inv()), True]]
        except sp.NonInvertibleMatrixError:
            raise LabError("Matriks ini tidak punya invers (determinannya 0).",
                   "err.matrix_no_inverse")
    elif op == "rank":
        out["rows"] = [["R", str(M.rank()), False]]
    elif op == "eig":
        if not M.is_square:
            raise LabError("Eigen hanya untuk matriks persegi.",
                   "err.matrix_square")
        rows = []
        for val, mult, vects in M.eigenvects():
            label = "R" if mult == 1 else f"R x{mult}"
            rows.append([label,
                         sp.latex(val) + " ; v = " + ", ".join(sp.latex(v) for v in vects),
                         True])
        if not rows:
            raise LabError("Eigen tidak ditemukan.", "err.eigen_none")
        out["rows"] = rows
    elif op == "rref":
        out["rows"] = [["R", sp.latex(M.rref()[0]), True]]
    elif op == "T":
        out["rows"] = [["R", sp.latex(M.T), True]]
    else:
        raise LabError("Operasi matriks tidak dikenal.", "err.matrix_op")
    return out


# ============================================================
# TOOL: pemecah ODE
# ============================================================
def tool_ode(d):
    raw = str(d.get("eq") or "").strip()
    if not raw:
        raise LabError("Persamaan diferensial kosong.", "err.expr_empty")
    if len(raw) > 200:
        raise LabError("Persamaan terlalu panjang.", "err.expr_long")
    y = sp.Function("y")

    def repl(m):
        n = len(m.group(1))
        # string utk sympify: simbol x lowercase dipetakan locals ke X
        return "Derivative(y(x), " + ", ".join(["x"] * n) + ")"

    raw = re.sub(r"y('+)", repl, raw)
    # y telanjang (bukan y(...) ) jadi y(x) biar sympify ngasilin ekspresi
    raw = re.sub(r"\by\b(?!\()", "y(x)", raw)
    if "=" in raw:
        lhs, rhs = raw.split("=", 1)
    else:
        lhs, rhs = raw, "0"
    try:
        L = sp.sympify(lhs, locals={"y": y, "x": X})
        R = sp.sympify(rhs, locals={"y": y, "x": X})
    except Exception as e:
        raise LabError(f"Persamaan tidak bisa dipahami: {e}", "err.expr_parse", str(e))
    eq = sp.Eq(L, R)
    if not eq.atoms(sp.Derivative):
        raise LabError("Persamaan harus memuat turunan y, contoh: y' + y = x",
                   "err.ode_needs_derivative")
    ics = {}
    raw_ic = str(d.get("ics") or "").strip()
    if raw_ic:
        for part in raw_ic.split(","):
            part = part.strip()
            if not part:
                continue
            m = re.fullmatch(r"y('*)\(\s*([-\d.]+)\s*\)\s*=\s*([-\d.eE+]+)", part)
            if not m:
                raise LabError(f"Syarat awal tidak valid: '{part}' (format: y(0)=1, y'(0)=2)",
                   "err.ode_ics", part)
            primes, x0, val = m.group(1), float(m.group(2)), float(m.group(3))
            if primes:
                ics[sp.Derivative(y(X), X, len(primes)).subs(X, x0)] = val
            else:
                ics[y(X).subs(X, x0)] = val
    try:
        sol = sp.dsolve(eq, y(X), ics=ics or None)
    except Exception as e:
        raise LabError(f"ODE ini belum bisa diselesaikan: {e}", "err.ode_unsolvable", str(e))
    return {"rows": [["y", sp.latex(sol.rhs), True]]}


# ============================================================
# TOOL: statistika deskriptif
# ============================================================
def tool_stats(d):
    raw = str(d.get("data") or "").strip()
    parts = [p for p in re.split(r"[,\s;]+", raw) if p]
    if not parts:
        raise LabError("Data kosong.", "err.data_empty")
    if len(parts) > 2000:
        raise LabError("Maksimal 2000 angka.", "err.data_max", "2000")
    try:
        nums = [float(p.replace(",", ".")) for p in parts]
    except ValueError:
        raise LabError("Ada nilai yang bukan angka.", "err.data_not_number")
    if any(not math.isfinite(v) for v in nums):
        raise LabError("Data harus angka berhingga.", "err.data_not_finite")
    n = len(nums)
    mean = sum(nums) / n
    snums = sorted(nums)
    median = (snums[n // 2] if n % 2 else (snums[n // 2 - 1] + snums[n // 2]) / 2)
    freq = {}
    for v in nums:
        freq[v] = freq.get(v, 0) + 1
    top = max(freq.values())
    modes = [k for k, c in freq.items() if c == top]
    mode_str = _fmt(modes[0]) if len(modes) == 1 else "multi"
    out = {
        "n": str(n), "mean": _fmt(mean), "median": _fmt(median),
        "mode": mode_str, "min": _fmt(snums[0]), "max": _fmt(snums[-1]),
        "sum": _fmt(sum(nums)),
    }
    if n >= 2:
        var_s = sum((v - mean) ** 2 for v in nums) / (n - 1)
        out["var_s"] = _fmt(var_s)
        out["std_s"] = _fmt(math.sqrt(var_s))
    return out


# ============================================================
# TOOL: termodinamika (gas ideal + carnot)
# ============================================================
def tool_thermo(d):
    mode = d.get("mode", "ideal")
    if mode == "ideal":
        known = {}
        for k, key in (("P", "p"), ("V", "v"), ("N", "n"), ("T", "t")):
            raw = str(d.get(key) or "").strip()
            if raw != "":
                known[k] = _num(raw, key, minv=0)
        solve = str(d.get("solve") or "").strip().upper()
        if solve not in ("P", "V", "N", "T"):
            raise LabError("Variabel yang dicari harus P, V, n, atau T.",
                   "err.thermo_var")
        if solve in known:
            raise LabError(f"'{solve}' sedang dicari, jadi kosongkan isian itu.",
                   "err.thermo_solve_clear", solve)
        if len(known) != 3:
            raise LabError("Isi tepat 3 nilai diketahui, 1 yang dicari dikosongkan.",
                       "err.thermo_fill")
        if solve == "P":
            val = known["N"] * R_GAS * known["T"] / known["V"]
        elif solve == "V":
            val = known["N"] * R_GAS * known["T"] / known["P"]
        elif solve == "N":
            val = known["P"] * known["V"] / (R_GAS * known["T"])
        else:
            val = known["P"] * known["V"] / (known["N"] * R_GAS)
        return {"rows": [[solve, _fmt(val), False]]}
    if mode == "carnot":
        th = _num(d.get("thot"), "Th", minv=0, allow_zero=False)
        tc = _num(d.get("tcold"), "Tc", minv=0)
        if tc >= th:
            raise LabError("Suhu dingin harus lebih kecil dari suhu panas.",
                   "err.thermo_tc")
        eta = 1 - tc / th
        return {"rows": [["eta", f"{eta:.6g}", False], ["eta_pct", f"{eta * 100:.4g} %", False]]}
    raise LabError("Mode termodinamika tidak dikenal.", "err.mode", "termodinamika")


# ============================================================
# TOOL: kuantum (de broglie, foton, fotolistrik)
# ============================================================
def tool_qm(d):
    mode = d.get("mode", "debr")
    if mode == "debr":
        m = _num(d.get("mass"), "m", minv=0, allow_zero=False)
        v = _num(d.get("vel"), "v", minv=0)
        lam = H_PLANCK / (m * v)
        return {"rows": [["lambda", f"{lam:.6g} m", False]]}
    if mode == "photon":
        f = _num(d.get("freq"), "f", minv=0, allow_zero=False)
        E = H_PLANCK * f
        lam = C_LIGHT / f
        return {"rows": [
            ["E_J", f"{E:.6g} J", False],
            ["E_eV", f"{E / Q_E:.6g} eV", False],
            ["lambda", f"{lam:.6g} m", False],
        ]}
    if mode == "photo":
        f = _num(d.get("freq"), "f", minv=0, allow_zero=False)
        phi_ev = _num(d.get("work"), "phi", minv=0)
        E = H_PLANCK * f
        ke = E - phi_ev * Q_E
        if ke <= 0:
            raise LabError("Energi foton kurang dari fungsi kerja: tidak ada emisi elektron.",
                   "err.qm_no_emission")
        return {"rows": [
            ["KE_J", f"{ke:.6g} J", False],
            ["KE_eV", f"{ke / Q_E:.6g} eV", False],
        ]}
    raise LabError("Mode kuantum tidak dikenal.", "err.mode", "kuantum")


# ============================================================
# TOOL: elektrostatika
# ============================================================
def tool_es(d):
    mode = d.get("mode", "coulomb")
    if mode == "coulomb":
        q1 = _num(d.get("q1"), "q1")
        q2 = _num(d.get("q2"), "q2")
        r = _num(d.get("r"), "r", minv=0, allow_zero=False)
        F = K_COULOMB * q1 * q2 / (r * r)
        kind = "tolak" if q1 * q2 > 0 else ("tarik" if q1 * q2 < 0 else "nol")
        return {"rows": [["F", f"{F:.6g} N", False], ["kind", kind, False]]}
    if mode == "field":
        q = _num(d.get("q1"), "q")
        r = _num(d.get("r"), "r", minv=0, allow_zero=False)
        E = K_COULOMB * q / (r * r)
        return {"rows": [["E", f"{E:.6g} N/C", False]]}
    if mode == "cap":
        a = _num(d.get("a"), "A", minv=0, allow_zero=False)
        dd = _num(d.get("d"), "d", minv=0, allow_zero=False)
        C = EPS0 * a / dd
        return {"rows": [["C", f"{C:.6g} F", False]]}
    raise LabError("Mode elektrostatika tidak dikenal.", "err.mode", "elektrostatika")


# ============================================================
# TOOL: relativitas
# ============================================================
def tool_rel(d):
    beta = _num(d.get("v"), "v", minv=0, maxv=0.999999)
    gamma = 1 / math.sqrt(1 - beta * beta)
    mode = d.get("mode", "gamma")
    rows = [["gamma", f"{gamma:.6g}", False]]
    if mode == "dilation":
        t0 = _num(d.get("t0"), "t0", minv=0)
        rows.append(["dt", f"{gamma * t0:.6g} s", False])
    elif mode == "contraction":
        l0 = _num(d.get("l0"), "L0", minv=0)
        rows.append(["L", f"{l0 / gamma:.6g} m", False])
    elif mode == "energy":
        m = _num(d.get("m"), "m", minv=0, allow_zero=False)
        E = gamma * m * C_LIGHT ** 2
        E0 = m * C_LIGHT ** 2
        rows += [
            ["E", f"{E:.6g} J", False],
            ["E0", f"{E0:.6g} J", False],
            ["K", f"{(E - E0):.6g} J", False],
        ]
    return {"rows": rows}


# ============================================================
# TOOL: gerak parabola (+ data plot)
# ============================================================
def tool_proj(d):
    v0 = _num(d.get("v0"), "v0", minv=0, allow_zero=False)
    ang = _num(d.get("angle"), "sudut", minv=0, maxv=90)
    h0 = _num(d.get("h0"), "h0", minv=0)
    g = _num(d.get("g"), "g", minv=0.01, maxv=100, allow_zero=False)
    th = math.radians(ang)
    vx = v0 * math.cos(th)
    vy = v0 * math.sin(th)
    disc = vy * vy + 2 * g * h0
    tof = (vy + math.sqrt(disc)) / g
    rng = vx * tof
    hmax = h0 + (vy * vy) / (2 * g)
    n = 240
    ts = np.linspace(0.0, tof, n)
    xs = (vx * ts).tolist()
    ys = (h0 + vy * ts - 0.5 * g * ts * ts).tolist()
    ys[-1] = 0.0
    return {"rows": [
        ["x_max", f"{rng:.6g} m", False],
        ["y_max", f"{hmax:.6g} m", False],
        ["t", f"{tof:.6g} s", False],
    ], "plot": {"x": xs, "y": ys}}


# ============================================================
# TOOL: fluida (hidrostatik, kontinuitas, bernoulli)
# ============================================================
def tool_hydro(d):
    mode = d.get("mode", "hstat")
    if mode == "hstat":
        rho = _num(d.get("rho"), "rho", minv=0, allow_zero=False)
        h = _num(d.get("h"), "h", minv=0)
        p = rho * G_EARTH * h
        return {"rows": [
            ["P_gauge", f"{p:.6g} Pa", False],
            ["P_abs", f"{p + 101325:.6g} Pa", False],
        ]}
    if mode == "cont":
        a1 = _num(d.get("a1"), "A1", minv=0, allow_zero=False)
        a2 = _num(d.get("a2"), "A2", minv=0, allow_zero=False)
        v1 = _num(d.get("v1"), "v1", minv=0)
        v2 = a1 * v1 / a2
        return {"rows": [["v2", f"{v2:.6g} m/s", False]]}
    if mode == "bern":
        rho = _num(d.get("rho"), "rho", minv=0, allow_zero=False)
        v1 = _num(d.get("v1"), "v1", minv=0)
        p1 = _num(d.get("p1"), "P1")
        p2 = _num(d.get("p2"), "P2")
        h1 = _num(d.get("h1"), "h1")
        h2 = _num(d.get("h2"), "h2")
        inner = v1 * v1 + 2 * G_EARTH * (h1 - h2) + 2 * (p1 - p2) / rho
        if inner < 0:
            raise LabError("Kombinasi nilai ini menghasilkan v2 imajiner: tidak fisik (cek tekanan/tinggi).",
                   "err.fluid_imaginary")
        v2 = math.sqrt(inner)
        return {"rows": [["v2", f"{v2:.6g} m/s", False]]}
    raise LabError("Mode fluida tidak dikenal.", "err.mode", "fluida")


TOOLS = {
    "integral": tool_integral,
    "matrix": tool_matrix,
    "ode": tool_ode,
    "stats": tool_stats,
    "thermo": tool_thermo,
    "qm": tool_qm,
    "es": tool_es,
    "rel": tool_rel,
    "proj": tool_proj,
    "hydro": tool_hydro,
}


# ============================================================
# GELOMBANG 2 — complex, taylor, modmath, entropy, poly,
#               heatexp, schwartz, optics, shm, emind
# ============================================================
def _complex_parse(d):
    re_ = _num(d.get("re"), "Re", allow_zero=True)
    im = _num(d.get("im"), "Im", allow_zero=True)
    return sp.Integer(0) + re_ + sp.I * im


def tool_complex(d):
    z = _complex_parse(d)
    mode = d.get("mode", "polar")
    if mode == "polar":
        r = abs(z)
        arg = sp.arg(z)
        return {"rows": [
            ["abs", f"{float(r):.6g}", False],
            ["arg_rad", f"{float(arg):.6g} rad", False],
            ["arg_deg", f"{float(arg) * 180 / math.pi:.6g} deg", False],
            ["polar", sp.latex(r) + r" \cdot e^{i" + sp.latex(arg) + "}", True],
        ]}
    if mode == "power":
        n = _num(d.get("n"), "n")
        if abs(n - round(n)) > 1e-9:
            raise LabError("Pangkat n harus bilangan bulat.", "err.int", "n")
        res = sp.nsimplify(z) ** int(round(n))
        return {"rows": [["z^n", sp.latex(sp.simplify(res)), True],
                         ["num", _fmt(complex(res).real) + (" +" if complex(res).imag >= 0 else " -") + f" {abs(complex(res).imag):.6g}i", False]]}
    if mode == "roots":
        n = _num(d.get("n"), "n", minv=1, maxv=24, allow_zero=False)
        n = int(round(n))
        r = abs(z)
        th = float(sp.arg(z))
        rr = r ** (1.0 / n)
        rows = []
        for k in range(n):
            a = (th + 2 * math.pi * k) / n
            val = complex(rr * math.cos(a), rr * math.sin(a))
            rows.append([f"w{k + 1}", _fmt(val.real) + (" +" if val.imag >= 0 else " -") + f" {abs(val.imag):.6g}i", False])
    return {"rows": rows}
    raise LabError("Mode bilangan kompleks tidak dikenal.", "err.mode", "kompleks")


def tool_taylor(d):
    expr = _expr(d.get("expr"), ("x",))
    x0 = _num(d.get("x0"), "x0")
    order = _num(d.get("order"), "orde", minv=1, maxv=14, allow_zero=False)
    order = int(round(order))
    try:
        ser = sp.series(expr, X, x0, order + 1).removeO()
    except Exception as e:
        raise LabError(f"Deret Taylor gagal: {e}", "err.taylor_fail", str(e))
    return {"rows": [["poly", sp.latex(ser), True]]}


def tool_modmath(d):
    mode = d.get("mode", "powmod")
    if mode == "powmod":
        a = _num(d.get("a"), "a")
        n = _num(d.get("n"), "n", minv=2)
        b = _num(d.get("b"), "b", minv=0)
        if abs(a - round(a)) > 1e-9 or abs(n - round(n)) > 1e-9 or abs(b - round(b)) > 1e-9:
            raise LabError("a, b, dan n harus bilangan bulat.", "err.int", "a, b, dan n")
        if b > 1e7:
            raise LabError("Pangkat b terlalu besar (maks 10.000.000).",
                   "err.exp_too_big", "10.000.000")
        val = pow(int(round(a)), int(round(b)), int(round(n)))
        return {"rows": [["res", str(val), False]]}
    if mode == "invmod":
        a = _num(d.get("a"), "a")
        n = _num(d.get("n"), "n", minv=2)
        if abs(a - round(a)) > 1e-9 or abs(n - round(n)) > 1e-9:
            raise LabError("a dan n harus bilangan bulat.", "err.int", "a dan n")
        a_i, n_i = int(round(a)), int(round(n))
        g = math.gcd(a_i % n_i, n_i)
        if g != 1:
            raise LabError(f"Invers modular tidak ada karena gcd(a, n) = {g} (harus 1).",
                   "err.modinv_gcd", g)
        val = pow(a_i, -1, n_i)
        return {"rows": [["inv", str(val), False], ["check", f"{a_i} x {val} = {a_i * val} = 1 (mod {n_i})", False]]}
    if mode == "gcd":
        a = _num(d.get("a"), "a")
        b = _num(d.get("b"), "b")
        if abs(a - round(a)) > 1e-9 or abs(b - round(b)) > 1e-9:
            raise LabError("a dan b harus bilangan bulat.", "err.int", "a dan b")
        ai, bi = abs(int(round(a))), abs(int(round(b)))
        g = math.gcd(ai, bi)
        l = (ai * bi // g) if g else 0
        return {"rows": [["gcd", str(g), False], ["lcm", str(l), False]]}
    if mode == "prime":
        n = _num(d.get("n"), "n", minv=2)
        if abs(n - round(n)) > 1e-9:
            raise LabError("n harus bilangan bulat.", "err.int", "n")
        ni = int(round(n))
        if ni > 10 ** 15:
            raise LabError("n terlalu besar (maks 10^15).", "err.n_too_big")
        val = sp.factorint(ni)
        parts = " . ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(val.items()))
        is_p = len(val) == 1 and list(val.values())[0] == 1
        return {"rows": [
            ["prime", "ya" if is_p else "bukan", False],
            ["factor", parts, False],
        ]}
    raise LabError("Mode modular tidak dikenal.", "err.mode", "modular")


def tool_entropy(d):
    raw = str(d.get("probs") or "").strip()
    parts = [p for p in re.split(r"[,\s;]+", raw) if p]
    if not parts:
        raise LabError("Daftar probabilitas kosong.", "err.data_empty")
    if len(parts) > 500:
        raise LabError("Maksimal 500 probabilitas.", "err.data_max", "500")
    try:
        ps = [float(p.replace(",", ".")) for p in parts]
    except ValueError:
        raise LabError("Ada nilai yang bukan angka.", "err.data_not_number")
    if any(p < 0 for p in ps):
        raise LabError("Probabilitas tidak boleh negatif.", "err.prob_negative")
    total = sum(ps)
    if abs(total - 1) > 1e-6:
        raise LabError(f"Jumlah probabilitas harus 1 (sekarang {total:.6g}).",
                   "err.prob_sum", f"{total:.6g}")
    H = -sum(p * math.log2(p) for p in ps if p > 0)
    k = len([p for p in ps if p > 0])
    hmax = math.log2(k) if k > 1 else 0.0
    return {"rows": [
        ["H", f"{H:.6g} bit", False],
        ["H_max", f"{hmax:.6g} bit", False],
        ["red", f"{max(0.0, hmax - H):.6g} bit", False],
        ["k", str(k), False],
    ]}


def tool_poly(d):
    raw = str(d.get("coeffs") or "").strip()
    # jalur baru: polinom ditulis utuh, mis. "x^2 - 5x + 6" (atau LaTeX saja,
    # dikonversi di sisi klien). Jalur koefisien lama tetap didukung penuh.
    expr_raw = str(d.get("expr") or "").strip()
    mode = d.get("mode", "roots")
    if expr_raw:
        # dukung penulisan implisit ala manusia: "5x", "(x+1)(x-1)", "2x^3(x+1)"
        s = re.sub(r"(\d)(\s*)x", r"\1*\2x", expr_raw, flags=re.IGNORECASE)
        s = re.sub(r"\)(\s*)x", r")*\1x", s, flags=re.IGNORECASE)
        s = re.sub(r"\)(\s*)\(", r")*\1(", s)
        s = re.sub(r"(?<!\w)x(\s*)\(", r"x*\1(", s, flags=re.IGNORECASE)
        e = _expr(s, ("x",))
        try:
            P = sp.Poly(e, X)
        except Exception:
            raise LabError(
                "Ini bukan polinom (cek pangkat/operasi, mis. integral simbolik "
                "dengan batas tak berangka).", "err.not_polynomial")
        if P.degree() > 12:
            raise LabError("Maksimal derajat 12.", "err.poly_degree")
    else:
        parts = [p for p in re.split(r"[,\s;]+", raw) if p]
        if not parts:
            raise LabError("Koefisien kosong.", "err.data_empty")
        if len(parts) > 9:
            raise LabError("Maksimal derajat 8 (9 koefisien).", "err.poly_coeffs_max")
        try:
            coeffs = [sp.Rational(p) if re.fullmatch(r"-?\d+", p) else sp.Rational(str(_num(p, "koefisien")))
                      for p in parts]
        except LabError:
            raise
        except Exception:
            raise LabError("Koefisien harus angka.", "err.data_not_number")
        if all(c == 0 for c in coeffs):
            raise LabError("Semua koefisien nol.", "err.poly_zero")
        P = sp.Poly(coeffs, X)
    if mode == "roots":
        try:
            roots = P.all_roots()
        except Exception as e:
            raise LabError(f"Akar tidak bisa dihitung: {e}", "err.roots_fail", str(e))
        rows = []
        for i, r_ in enumerate(roots):
            numeric = None
            try:
                numeric = complex(sp.N(r_, 12))
                if abs(numeric.imag) < 1e-12:
                    disp = _fmt(numeric.real)
                else:
                    disp = _fmt(numeric.real) + (" +" if numeric.imag >= 0 else " -") + f" {abs(numeric.imag):.6g}i"
            except Exception:
                disp = sp.latex(r_)
            rows.append([f"x{i + 1}", disp, False])
    if mode == "factor":
        f = sp.factor(P.as_expr())
        rows = [["R", sp.latex(f), True]]
    return {"rows": rows}


def tool_heatexp(d):
    mode = d.get("mode", "heat")
    if mode == "heat":
        m = _num(d.get("m"), "m", minv=0, allow_zero=False)
        c = _num(d.get("c"), "c", minv=0, allow_zero=False)
        t1 = _num(d.get("t1"), "T1")
        t2 = _num(d.get("t2"), "T2")
        Q = m * c * (t2 - t1)
        return {"rows": [
            ["Q", f"{Q:.6g} J", False],
            ["dir", "serap" if Q > 0 else ("lepas" if Q < 0 else "nol"), False],
        ]}
    if mode == "expand":
        l0 = _num(d.get("l0"), "L0", minv=0, allow_zero=False)
        alpha = _num(d.get("alpha"), "alpha", minv=0)
        dt = _num(d.get("dt"), "dT")
        dl = alpha * l0 * dt
        return {"rows": [["dL", f"{dl:.6g} m", False]]}
    if mode == "latent":
        m = _num(d.get("m"), "m", minv=0, allow_zero=False)
        L = _num(d.get("latent"), "L", minv=0, allow_zero=False)
        return {"rows": [["Q", f"{m * L:.6g} J", False]]}
    raise LabError("Mode kalor tidak dikenal.", "err.mode", "kalor")


M_SUN = 1.98892e30
G_NEWTON = 6.67430e-11


def tool_schwartz(d):
    msun = _num(d.get("msun"), "M (M sun)", minv=0, allow_zero=False)
    M = msun * M_SUN
    rs = 2 * G_NEWTON * M / (C_LIGHT ** 2)
    rows = [["rs", f"{rs:.6g} m", False]]
    r_raw = str(d.get("r") or "").strip()
    if r_raw != "":
        r = _num(r_raw, "r", minv=0, allow_zero=False)
        if r <= rs:
            raise LabError("r harus lebih besar dari jari-jari Schwarzschild (di luar horizon).",
                   "err.rel_r")
        dil = math.sqrt(1 - rs / r)
        rows.append(["dil", f"{dil:.6g}", False])
        rows.append(["dt_ratio", f"{1 / dil:.6g}", False])
        rows.append(["vesc", f"{math.sqrt(2 * G_NEWTON * M / r):.6g} m/s", False])
    return {"rows": rows}


def tool_optics(d):
    mode = d.get("mode", "snell")
    if mode == "snell":
        n1 = _num(d.get("n1"), "n1", minv=1)
        n2 = _num(d.get("n2"), "n2", minv=1)
        th1 = _num(d.get("th1"), "tetha1", minv=0, maxv=89.99)
        s = n1 * math.sin(math.radians(th1)) / n2
        if s > 1:
            return {"rows": [["tir", "ya", False]]}
        th2 = math.degrees(math.asin(s))
        crit = None
        if n1 > n2:
            crit = math.degrees(math.asin(n2 / n1))
        rows = [["th2", f"{th2:.6g} deg", False]]
        if crit is not None:
            rows.append(["crit", f"{crit:.6g} deg", False])
    return {"rows": rows}
    if mode == "lens":
        f = _num(d.get("f"), "f", allow_zero=False)
        do = _num(d.get("do"), "do", minv=0, allow_zero=False)
        if f == do:
            raise LabError("Jarak benda sama dengan fokus: bayangan di tak hingga.",
                   "err.optics_infinity")
        di = 1 / (1 / f - 1 / do)
        mag = -di / do
        return {"rows": [
            ["di", f"{di:.6g} m", False],
            ["m", f"{mag:.6g}x", False],
            ["kind", "nyata" if di > 0 else "maya", False],
        ]}
    if mode == "dslit":
        lam = _num(d.get("lam"), "lambda", minv=0, allow_zero=False)
        dd = _num(d.get("d"), "d", minv=0, allow_zero=False)
        L = _num(d.get("L"), "L", minv=0, allow_zero=False)
        return {"rows": [["dy", f"{lam * L / dd:.6g} m", False]]}
    raise LabError("Mode optik tidak dikenal.", "err.mode", "optik")


def tool_shm(d):
    mode = d.get("mode", "mass")
    if mode == "mass":
        m = _num(d.get("m"), "m", minv=0, allow_zero=False)
        k = _num(d.get("k"), "k", minv=0, allow_zero=False)
        T = 2 * math.pi * math.sqrt(m / k)
        return {"rows": [["T", f"{T:.6g} s", False], ["f", f"{1 / T:.6g} Hz", False],
                         ["omega", f"{2 * math.pi / T:.6g} rad/s", False]]}
    if mode == "pend":
        L = _num(d.get("L"), "L", minv=0, allow_zero=False)
        g = _num(d.get("g"), "g", minv=0.01, maxv=100, allow_zero=False)
        T = 2 * math.pi * math.sqrt(L / g)
        return {"rows": [["T", f"{T:.6g} s", False], ["f", f"{1 / T:.6g} Hz", False]]}
    if mode == "energy":
        A = _num(d.get("A"), "A", minv=0)
        k = _num(d.get("k"), "k", minv=0, allow_zero=False)
        E = 0.5 * k * A * A
        return {"rows": [["E", f"{E:.6g} J", False]]}
    raise LabError("Mode getaran tidak dikenal.", "err.mode", "getaran")


def tool_emind(d):
    mode = d.get("mode", "faraday")
    if mode == "faraday":
        N = _num(d.get("N"), "N", minv=1, allow_zero=False)
        dphi = _num(d.get("dphi"), "dPhi/dt", allow_zero=True)
        return {"rows": [["EMF", f"{N * dphi:.6g} V", False]]}
    if mode == "trafo":
        v1 = _num(d.get("v1"), "V1")
        n1 = _num(d.get("n1"), "N1", minv=1, allow_zero=False)
        n2 = _num(d.get("n2"), "N2", minv=1, allow_zero=False)
        return {"rows": [["V2", f"{v1 * n2 / n1:.6g} V", False],
                         ["kind", "step-up" if n2 > n1 else ("step-down" if n2 < n1 else "1:1"), False]]}
    if mode == "motional":
        B = _num(d.get("B"), "B")
        v = _num(d.get("v"), "v")
        L = _num(d.get("L"), "L", minv=0, allow_zero=False)
        return {"rows": [["EMF", f"{B * v * L:.6g} V", False]]}
    raise LabError("Mode induksi tidak dikenal.", "err.mode", "induksi")


TOOLS["complex"] = tool_complex
TOOLS["taylor"] = tool_taylor
TOOLS["modmath"] = tool_modmath
TOOLS["entropy"] = tool_entropy
TOOLS["poly"] = tool_poly
TOOLS["heatexp"] = tool_heatexp
TOOLS["schwartz"] = tool_schwartz
TOOLS["optics"] = tool_optics
TOOLS["shm"] = tool_shm
TOOLS["emind"] = tool_emind


def run_tool(tool, data):
    fn = TOOLS.get(str(tool or "").strip())
    if not fn:
        raise LabError(f"Tool '{tool}' tidak dikenal.", "err.tool", tool)
    try:
        return fn(data if isinstance(data, dict) else {})
    except LabError:
        raise               # error input yang disengaja: pesan rapi
    except Exception as e:
        # bug internal (TypeError/AttributeError/KeyError/FunctionClass dsb)
        # JANGAN tampilkan raw python ke user (bug_reports2.md section 13)
        import traceback
        traceback.print_exc()
        raise LabError(
            "Terjadi kesalahan internal saat menghitung — lapor ke kami "
            "beserta rumusnya ya. (id: " +
            re.sub(r"[^A-Za-z0-9]", "", type(e).__name__)[:24] + ")",
            "err.internal", type(e).__name__)
