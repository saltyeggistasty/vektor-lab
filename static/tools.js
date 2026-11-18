/* ============================================================
   NABLA LAB TOOLS, panel generik untuk semua tool card baru.
   Satu section #tool dipakai bareng: registry TOOLS menentukan input,
   payload, dan cara render hasil (rows/latex/plot). Label i18n diambil
   dr JSON (grup tools.*), fallback Indonesia. MURNI UI, hitung di
   backend (mathlab.py) via /api/lab.
   v2: input MathLive (LaTeX) utk ekspresi, konversi LaTeX->ASCII,
   preview matriks, kotak contoh penggunaan (KaTeX), mode kalkulus
   lengkap (integral/limit/turunan/deret/eksponensial-log),
   polinom ditulis utuh (mis. x^2-5x+6).
   ============================================================ */
(function () {
  "use strict";

  const sec = document.getElementById("tool");
  if (!sec || typeof $ !== "function") return;

  const t = (k, fb) => (window.I18N ? I18N.t(k, fb) : fb);

  /* pesan error → bahasa aktif: backend kirim errKey+errArgs, error client
     (parser graphers) dicocokkan dgn pola. Fallback = teks asli. */
  function errText(j) {
    if (j && j.errKey) {
      let s = t(j.errKey, j.error || "");
      (j.errArgs || []).forEach((a, i) => { s = s.split("{" + i + "}").join(a); });
      return s;
    }
    const m = (j && j.error) || "";
    const MAP = [
      [/^Variabel belum diisi:\s*(.+)$/, "err.var_not_set"],
      [/^Variabel tidak dikenal:\s*(.+)$/, "err.unknown_var"],
      [/^Simbol tidak dikenal:\s*(.+)$/, "err.unknown_symbols"],
      [/^Fungsi (?:kompleks )?tidak dikenal:\s*(.+)$/, "err.unknown_func"],
      [/^Karakter tidak dikenal:\s*(.+)$/, "err.bad_char"],
      [/^Sisa token tak terpakai\.?$/, "err.leftover"],
      [/^Kurung tutup hilang\.?$/, "err.missing_paren"],
      [/^Ekspresi berakhir tak wajar\.?$/, "err.unterminated"],
      [/^Token tak terduga:\s*(.+)$/, "err.unexpected"],
      [/^Ekspresi kosong\.?$/, "err.expr_empty"],
      [/^Ekspresi terlalu panjang\.?$/, "err.expr_long"],
      [/^Ekspresi mengandung kata yang tidak diizinkan\.?$/, "err.expr_forbidden"],
      [/^Ekspresi tidak bisa dipahami:\s*(.+)$/, "err.expr_parse"],
      [/^Mode '.*' tidak dikenal\.?$/, "err.mode"],
      [/^Engine error:\s*(.+)$/, "err.engine_error"],
    ];
    for (const [re, key] of MAP) {
      const mm = m.match(re);
      if (mm) {
        let s = t(key, m);
        for (let i = 1; i < mm.length; i++) s = s.split("{" + (i - 1) + "}").join(mm[i]);
        return s;
      }
    }
    return m;
  }

  /* ---------- operator kalkulus LaTeX → panggilan sympy ----------
     Destilasi dari eval_calculus_latex() di vectorcalc.py (mesin
     Multivariable Calculator): \int_{a}^{b} body d<var>, \int body d<var>,
     \sum_{v=a}^{b} body, \lim_{v\to a} body, \infty → oo.
     Hasil: string berisi integrate()/summation()/limit() yang paham
     buat sympify backend.                                      */
  function readGroup(s, i) {
    if (s[i] !== "{") return null;
    let d = 0;
    for (let j = i; j < s.length; j++) {
      if (s[j] === "{") d++;
      else if (s[j] === "}") { d--; if (!d) return [s.slice(i + 1, j), j + 1]; }
    }
    return null;
  }

  /* ambil satu "operand body": {seimbang} | makro+grup | (kurung)[^pangkat]
     | token+pangkat+SUBSKRIP (x_i satu kesatuan!) — kurung IKUT membawa
     pangkat (\lim .. (1+1/x)^x) */
  function grabBody(str) {
    let i = 0;
    while (i < str.length && str[i] === " ") i++;
    if (str[i] === "{") {
      const g = readGroup(str, i);
      if (g) return { body: g[0], len: g[1] };
    }
    const m = /^(\\[a-zA-Z]+(?:\s*\{(?:[^{}]|\{[^{}]*\})*\})*|\((?:[^()]|\([^()]*\))*\)(?:\s*\^\s*(?:\{[^{}]*\}|[A-Za-z0-9.]+))?|[A-Za-z0-9.]+(?:\s*\^\s*(?:\{(?:[^{}]|\{[^{}]*\})*\}|[A-Za-z0-9.]+))?(?:\s*_\s*(?:\{[^{}]*\}|[A-Za-z0-9.]+))?)/.exec(str.slice(i));
    if (m) return { body: m[1], len: i + m[1].length };
    return { body: "", len: i };
  }

  /* ---- normalizer fungsi berpangkat (bug K1) ----
     \sin^2x / \sin^{2}x / \sin^2(x) / \sin^2 2x → (sin(x))^{2} dgn
     ARGUMENT RUN (faktor implisit beruntun, berhenti di fungsi lain,
     +/-, koma, penutup, \cdot/\times). \sin^{-1}x = INVERSE (asin) —
     keputusan desain (bug_reports2.md P28). Fungsi telanjang
     (\sin 2x → sin(2x)) ikut dibungkus. */
  const FN_ALT = "arcsin|arccos|arctan|arccot|arcsec|arccsc|sinh|cosh|tanh|asin|acos|atan|sin|cos|tan|cot|sec|csc|ln|log|exp";
  const FNSET = new Set(FN_ALT.split("|"));
  const INVMAP = { sin: "asin", cos: "acos", tan: "atan", cot: "acot",
    sec: "asec", csc: "acsc", sinh: "asinh", cosh: "acosh", tanh: "atanh" };

  function grabArgRun(str) {
    /* run faktor implisit: makro, (grup), {grup}, angka, huruf, ^p, _s */
    let i = 0, got = false;
    while (i < str.length) {
      const c = str[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === "+" || c === "-") { if (got) break; i++; continue; }
      if (c === "(") {
        let d = 0, j = i;
        for (; j < str.length; j++) {
          if (str[j] === "(") d++;
          else if (str[j] === ")") { d--; if (!d) { j++; break; } }
        }
        got = true; i = j; continue;
      }
      if (c === "{") {
        const g = readGroup(str, i);
        if (!g) { i++; continue; }
        got = true; i = g[1]; continue;
      }
      if (c === "^" && got) {
        let j = i + 1;
        if (str[j] === "{") {
          const g = readGroup(str, j);
          if (!g) break;
          i = g[1]; continue;
        }
        i = j + 1; continue;
      }
      if (c === "_" && got) {
        let j = i + 1;
        if (str[j] === "{") {
          const g = readGroup(str, j);
          if (!g) break;
          i = g[1]; continue;
        }
        i = j + 1; continue;
      }
      if (c === "\\") {
        const mm = /^\\([a-zA-Z]+)/.exec(str.slice(i));
        if (!mm) break;   /* orphan backslash (\, dsb) → stop, jangan ikut */
        if (FNSET.has(mm[1])) break;
        if (mm[1] === "cdot" || mm[1] === "times" || mm[1] === "div") break;
        let j = i + mm[0].length;
        while (str[j] === "{") {
          const g = readGroup(str, j);
          if (!g) break;
          j = g[1];
        }
        got = true; i = j; continue;
      }
      if (/[0-9.]/.test(c)) {
        let j = i;
        while (j < str.length && /[0-9.]/.test(str[j])) j++;
        got = true; i = j; continue;
      }
      if (/[a-zA-Z]/.test(c)) { got = true; i++; continue; }
      break;
    }
    return got ? { arg: str.slice(0, i).trim(), len: i } : null;
  }

  function _normalizeFnOnce(s) {
    const re = new RegExp("\\\\(" + FN_ALT + ")(?![a-zA-Z])", "g");
    let out = "", last = 0, m, guard = 0;
    while (guard++ < 50 && (m = re.exec(s))) {
      const fn = m[1];
      const after = m.index + m[0].length;
      const rest = s.slice(after);
      /* eksponen tak-kurung = angka / SATU huruf — jangan serakah */
      const em = /^\s*\^\s*(?:\{([^{}]*)\}|([0-9]+|[A-Za-z]))/.exec(rest);
      let exp = null, bodyStr = rest;
      if (em) {
        exp = em[1] != null ? em[1] : em[2];
        bodyStr = rest.slice(em[0].length);
      }
      /* \sin(x) TANPA pangkat → biarkan (macro rule yg proses);
         \sin^2(x) dgn pangkat → tetap ditulis ulang */
      if (!em && /^\s*\(/.test(bodyStr)) continue;
      const arg = grabArgRun(bodyStr);
      if (!arg || !arg.arg) continue;
      /* nama inverse arcsin-style → asin-style (sympify/mathjs paham) */
      const INVNAME = { arcsin: "asin", arccos: "acos", arctan: "atan",
        arccot: "acot", arcsec: "asec", arccsc: "acsc" };
      const name = INVNAME[fn] || fn;
      let repl;
      if (exp === "-1" && INVMAP[fn])
        repl = "\\" + INVMAP[fn] + "(" + arg.arg + ")";
      else if (exp != null)
        repl = name + "(" + arg.arg + ")^{" + exp + "}";
      else
        repl = name + "(" + arg.arg + ")";
      /* perkalian implisit: huruf/angka sebelum makro → x·arctan(x) */
      const prevCh = m.index > 0 ? s[m.index - 1] : "";
      if (/[0-9a-zA-Z)\]]/.test(prevCh)) repl = "*" + repl;
      out += s.slice(last, m.index) + repl;
      last = after + (em ? em[0].length : 0) + arg.len;
      re.lastIndex = last;
    }
    out += s.slice(last);
    return out;
  }

  function normalizeFnPowers(s) {
    for (let k = 0; k < 8; k++) {
      const s2 = _normalizeFnOnce(s);
      if (s2 === s) break;
      s = s2;
    }
    return s;
  }

  /* ---- calculus2sympy(s, uneval) ----
     uneval=false (default, perilaku lama): operator -> panggilan sympy
     yang LANGSUNG dievaluasi (integrate/summation/limit).
     uneval=true (tool Integrals & Limits): operator -> objek sympy
     TAK-EVALUASI (Integral/Sum/Limit/Derivative/Product, huruf kapital)
     + aturan turunan \frac{d}{dx} yang dulu gak ada. Backend
     (mathlab.tool_integral) mendeteksi kelas ini & menerapkan operasi
     PERSIS SEKALI -> bug dobel-apply (\int diinput + mode integral) dan
     "Unknown symbols: d, dx" beres bersamaan. */
  /* operand turunan: ambil sampai +/- tingkat atas (\frac{d}{dx} x e^x
     → body "x e^x" utuh, tapi "\frac{d}{dx} x^3 + 1" berhenti di +) */
  function grabTillPlus(str) {
    let i = 0, depth = 0, got = false;
    while (i < str.length) {
      const c = str[i];
      if (c === "(" || c === "{") { depth++; got = true; i++; continue; }
      if (c === ")" || c === "}") { depth--; got = true; i++; continue; }
      if (depth === 0 && got && (c === "+" || c === "-")) break;
      if (depth === 0 && !got && (c === "+" || c === "-")) { i++; continue; }
      if (!/\s/.test(c)) got = true;
      i++;
    }
    return { body: str.slice(0, i).trim(), len: i };
  }

  function calculus2sympy(s, uneval) {
    s = s.replace(/\\infty/g, "oo");
    /* placeholder MathLive yang belum diisi -> kosong (biar error-nya
       "Ekspresi kosong" yang jelas, bukan sampah \placeholder{} ) */
    s = s.replace(/\\placeholder\{([^{}]*)\}/g, "$1");
    s = s.replace(/\\placeholder/g, "");
    /* \limits dekorasi (\lim\limits_{..}) & \mathrm{d} -> marker d biasa */
    s = s.replace(/\\limits/g, "");
    s = s.replace(/\\mathrm\s*\{\s*d\s*\}/g, "d");
    /* bar evaluasi — SEMUA varian → opd subs_deriv: \left.B\right|_{x=a},
       B\bigm{|}_{x=a}, B\bigm|_{x=a}, B\big|_{x=a}, B|_{x=a} (template
       menu insert derivative pakai \bigm{|}, versi ketik pakai \bigm|).
       Body = semua sebelum bar. */
    if (uneval) {
      const bm = /([\s\S]*?)\s*(?:\\[bB]ig[lmr]*\s*)?(?:\{\s*\|?\s*\}|\|)\s*_\{\s*([a-z])\s*=\s*([^{}]*?)\s*\}/.exec(s);
      if (bm && bm[1].trim()) {
        const innerP = la2plain(bm[1], { unevaluated: true });
        if (innerP.startsWith("__NABLA_ERR__")) return innerP;
        const inner = innerP.startsWith("__NABLA_OP__")
          ? JSON.parse(innerP.slice(12)) : { op: "eval", body: innerP };
        const pt = la2plain(bm[3]);
        const opd = { op: "subs_deriv", sub: inner, var: bm[2], point: pt };
        s = s.slice(0, bm.index) + "__NABLA_OP__" + JSON.stringify(opd) +
          s.slice(bm.index + bm[0].length);
      }
      /* paste baris contoh: "\int_0^3 ... dx \approx 1.84" / "f' = ..., ..."
         → ambil sisi KIRI tanda = / \approx tingkat atas (dalam kurung
         & kurung keriting di-skip; macro di-skip TANPA melompati brace
         sesudahnya) */
      for (let i = 0, depth = 0; i < s.length; i++) {
        const c = s[i];
        if (s.startsWith("\\approx", i)) {
          if (s.slice(0, i).trim()) s = s.slice(0, i);
          else s = s.slice(i + 7);
          break;
        }
        if (c === "{" || c === "(") { depth++; continue; }
        if (c === "}" || c === ")") { depth--; continue; }
        if (depth !== 0) continue;
        if (c === "=") {
          if (s.slice(0, i).trim()) s = s.slice(0, i);
          else s = s.slice(i + 1);
          break;
        }
        if (c === "\\") { i++; while (i < s.length && /[a-zA-Z]/.test(s[i])) i++; i--; }
      }
    }
    /* \left \right dekorasi murni — dibuang SETELAH bar transform &
       SEBELUM grabBody biar \left(1+\frac{1}{x}\right)^x kebaca satu
       operand utuh. (?![a-z]): jangan makan \rightarrow! */
    s = s.replace(/\\left(?![a-z])|\\right(?![a-z])/g, "");
    /* batas \int_1^{2} / \int_{1}^{2} / \int_0^\infty (makro & oo!)
       dinormalisasi ke kurung */
    s = s.replace(/\\int_(?:\{([^{}]*)\}|(\\[a-zA-Z]+|oo|[^\s^]))\s*\^\s*(?:\{([^{}]*)\}|(\\[a-zA-Z]+|oo|[^\s,;)]))/g,
      (m, a, b, c, d) => "\\int_{" + (a != null ? a : b) + "}^{" + (c != null ? c : d) + "}");

    if (!uneval) {
      /* integral tentu: body s/d tanda d<var> */
      s = s.replace(/\\int_\{([^{}]*)\}\^\{([^{}]*)\}\s*([\s\S]*?)\s*d([a-z])\b/g,
        (m, lo, hi, body, v) => `integrate((${body}),(${v},${lo},${hi}))`);
      /* integral tak tentu */
      s = s.replace(/\\int\s*([\s\S]*?)\s*d([a-z])\b/g,
        (m, body, v) => `integrate((${body}),(${v}))`);
      /* deret berhingga/tak berhingga (batas atas tak-kurung: angka /
         satu huruf — jangan serakah makan body) */
      for (let guard = 0; guard < 10; guard++) {
        const m = /\\sum_\{([a-zA-Z]\w*)\s*=\s*([^{}]+)\}\s*\^\s*(?:\{([^{}]+)\}|(\d+(?:\.\d+)?|[A-Za-z]))/.exec(s);
        if (!m) break;
        const v = m[1], lo = m[2], hi = m[3] != null ? m[3] : m[4];
        const rest = s.slice(m.index + m[0].length);
        const gb = grabBody(rest);
        s = s.slice(0, m.index) + `summation((${gb.body}),(${v},${lo},${hi}))` + rest.slice(gb.len);
      }
      /* limit */
      for (let guard = 0; guard < 10; guard++) {
        const m = /\\lim_(?:\{([^{}]*)\}|(\S))/.exec(s);
        if (!m) break;
        const sub = m[1] != null ? m[1] : m[2];
        const seg = sub.split(/\\rightarrow|\\to/);
        const v = (seg[0] || "x").trim();
        const at = (seg[1] || "0").trim();
        const rest = s.slice(m.index + m[0].length);
        const gb = grabBody(rest);
        s = s.slice(0, m.index) + `limit((${gb.body}),(${v},${at}))` + rest.slice(gb.len);
      }
      return s;
    }

    /* ================= MODE UNEVALUATED =================
       Operator dikirim sebagai JSON TERSTRUKTUR (__NABLA_OP__ + op_data):
       backend (mathlab._build_op) membangun objek sympy SECARA
       PROGRAMATIK -> sympify gak pernah mengevaluasi operator di muka
       (Derivative otomatis ter-evaluasi oleh sympify = fitur titik
       evaluasi/orde bisa rusak). Body dikonversi rekursif. */
    /* multi/contour integral & lingkungan LaTeX (matriks, cases, align)
       -> sentinel "belum didukung" (backend terjemahin jadi pesan bersih,
       bukan parse error mentah 'pmatrix}1 & ...') */
    if (/\\iint|\\iiint|\\oint|\\begin\{/.test(s))
      return "__NABLA_ERR__:int_unsupported";

    /* --- turunan (\frac{d}{dx}, \frac{d^n}{dx^n}, \partial, \frac{d f}{dx}) */
    let dFrom = 0;
    for (let guard = 0; guard < 10; guard++) {
      const m = /\\[dtc]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/.exec(s.slice(dFrom));
      if (!m) break;
      const at = dFrom + m.index;
      const num = m[1].trim(), den = m[2].trim();
      /* numerator: "d", "d^2", ATAU "d <body>" (\frac{d x^3}{dx}) */
      const numM = /^(d|\\partial)(?:\^\s*\{?\s*(\d+)\s*\}?)?\s*([\s\S]*)$/.exec(num);
      const denD = /^(?:d|\\partial)\s*[a-z](?:\s*\^\s*\{?\s*(\d+)\s*\}?)?(?:\s*(?:d|\\partial)\s*[a-z])*$/.test(den);
      if (!numM || !denD) { dFrom = at + 4; continue; }
      const order = numM[2]
        || (den.match(/\^\s*\{?\s*(\d+)/) || [])[1] || "1";
      const dd = den.replace(/\\partial/g, "d");
      const vms = [...dd.matchAll(/d\s*([a-z])(?:\s*\^\s*\{?\s*(\d+)\s*\}?)?/g)];
      const v = vms[0][1];
      /* body: di numerator ("d x^3") atau sisanya (grabTillPlus: operand
         utuh s.d. +/- tingkat atas) */
      const numBody = numM[3];
      let rest = s.slice(at + m[0].length);
      let bodyLa, after;
      if (numBody) { bodyLa = numBody; after = rest; }
      else {
        const gb = grabTillPlus(rest);
        if (!gb.body) break;
        bodyLa = gb.body; after = rest.slice(gb.len);
      }
      /* eval-bar TANPA pipe (paste bisa buang \bigm{|}): _{v=pt} di ujung
         body → dipisah jadi titik evaluasi (subs_deriv) */
      let evalPt = null;
      const ebm = /\s*_\{\s*([a-z])\s*=\s*([^{}]*?)\s*\}\s*$/.exec(bodyLa);
      if (ebm) {
        evalPt = { var: ebm[1], point: ebm[2] };
        bodyLa = bodyLa.slice(0, ebm.index);
      }
      const bodyP = la2plain(bodyLa, { unevaluated: true });
      if (bodyP.startsWith("__NABLA_ERR__")) return bodyP;
      const opd = { op: "derivative" };
      /* body bisa jadi operator NESTED (marker) → kirim sbg objek, BUKAN
         string (string = bocor ke sympify = "forbidden words") */
      if (bodyP.startsWith("__NABLA_OP__"))
        opd.body = JSON.parse(bodyP.slice(12));
      else
        opd.body = bodyP;
      if (vms.length > 1)
        /* multi-var (\partial x \partial y): tiap var + orde-nya */
        opd.vars = vms.map(mm => [mm[1], Number(mm[2] || 1)]);
      else
        { opd.var = v; opd.order = Number(order) || 1; }
      /* sisa ekspresi (+ 1 dsb) = penambah setelah operasi (backend) */
      const extraP = la2plain(after, { unevaluated: true });
      if (extraP.startsWith("__NABLA_ERR__")) return extraP;
      if (extraP) {
        opd.extra = extraP.startsWith("__NABLA_OP__")
          ? JSON.parse(extraP.slice(12)) : extraP;
      }
      if (evalPt) {
        /* body dievaluasi di titik → bungkus subs_deriv */
        const opd2 = { op: "subs_deriv", sub: opd, var: evalPt.var,
                       point: evalPt.point };
        return "__NABLA_OP__" + JSON.stringify(opd2);
      }
      return "__NABLA_OP__" + JSON.stringify(opd);
    }

    /* --- limit (termasuk satu sisi \to a^{+} / \to a^-) --- */
    {
      const m = /\\lim_\{((?:[^{}]|\{[^{}]*\})*)\}|\\lim_(\S)/.exec(s);
      if (m) {
        let sub = m[1] != null ? m[1] : m[2];
        let dir = "";
        const dm = /^(.*?)\s*\^\s*\{?\s*([+-])\s*\}?$/.exec(sub);
        if (dm) { sub = dm[1]; dir = dm[2]; }
        const seg = sub.split(/\\rightarrow|\\to/);
        const v = (seg[0] || "x").trim();
        const at = (seg[1] || "0").trim();
        const rest = s.slice(m.index + m[0].length);
        const gb = grabTillPlus(rest);   /* body run utuh (frac×integral dsb) */
        const bodyP = la2plain(gb.body, { unevaluated: true });
        if (bodyP.startsWith("__NABLA_ERR__")) return bodyP;
        const opd = { op: "limit", var: v, at: la2plain(at) };
        if (bodyP.startsWith("__NABLA_OP__"))
          opd.body = JSON.parse(bodyP.slice(12));
        else
          opd.body = bodyP;
        if (dir) opd.dir = dir;
        const extraP = la2plain(rest.slice(gb.len), { unevaluated: true });
        if (extraP.startsWith("__NABLA_ERR__")) return extraP;
        if (extraP) {
          opd.extra = extraP.startsWith("__NABLA_OP__")
            ? JSON.parse(extraP.slice(12)) : extraP;
        }
        return "__NABLA_OP__" + JSON.stringify(opd);
      }
    }
    
/* --- integral (satu per ekspresi; nested -> sentinel) --- */
    {
      const m = /\\int(?:_\{([^{}]*)\}\^\{([^{}]*)\})?/.exec(s);
      const hasOuterSum = m && /\\(sum|prod)_/.test(s.slice(0, m.index));
      if (m && !hasOuterSum) {
        const rest = s.slice(m.index + m[0].length);
        /* marker diferensial d<var>: d yang GAK diawali { / \ (dalam
           \frac{d}{dx} dsb) — \mathrm{d} sudah dinormalkan di atas */
        const dm = /(?<![{/\\])d([a-z])(?![a-zA-Z])/.exec(rest);
        if (!dm) return "__NABLA_ERR__:int_missing_dx";
        /* nested \int sebelum marker (\int_0^1 \int_0^x y dy dx) ->
           pesan eksplisit (parser baris gak sanggup nested) */
        const innerInt = rest.indexOf("\\int");
        if (innerInt !== -1 && innerInt < dm.index)
          return "__NABLA_ERR__:int_unsupported";
        const bodyLa = rest.slice(0, dm.index);
        const bodyP = la2plain(bodyLa, { unevaluated: true });
        if (bodyP.startsWith("__NABLA_ERR__")) return bodyP;
        const opd = { op: "integral", var: dm[1] };
        /* body bisa operator NESTED (marker) → objek, bukan string */
        if (bodyP.startsWith("__NABLA_OP__"))
          opd.body = JSON.parse(bodyP.slice(12));
        else
          opd.body = bodyP;
        if (m[1] != null) {
          opd.has_bounds = true;
          /* bound dikonversi la2plain (\pi→pi, \frac{\pi}{2}→((pi)/(2)))
             biar backend _bound gak ketemu backslash */
          opd.a = la2plain(m[1]);
          opd.b = la2plain(m[2]);
        }
        /* sisa setelah diferensial (+ 1 dsb) = penambah (backend) */
        const extraP = la2plain(rest.slice(dm.index + dm[0].length),
                                { unevaluated: true });
        if (extraP.startsWith("__NABLA_ERR__")) return extraP;
        if (extraP) {
          opd.extra = extraP.startsWith("__NABLA_OP__")
            ? JSON.parse(extraP.slice(12)) : extraP;
        }
        return "__NABLA_OP__" + JSON.stringify(opd);
      }
    }

    /* --- sum & product (berhingga / tak berhingga / simbolik) ---
       batas atas TANPA kurung (^5n) = angka atau SATU huruf saja —
       jangan serakah (dulu "5n" kebaca batas -> body kosong ->
       "Empty expression") */
    {
      const m = /\\(sum|prod)_\{([a-zA-Z]\w*)\s*=\s*([^{}]+)\}\s*\^\s*(?:\{([^{}]+)\}|(\d+(?:\.\d+)?|[A-Za-z]))/.exec(s);
      if (m) {
        const v = m[2], lo = m[3], hi = m[4] != null ? m[4] : m[5];
        const rest = s.slice(m.index + m[0].length);
        const gb = grabTillPlus(rest);   /* body run utuh (k*2^k dsb) */
        const bodyP = la2plain(gb.body, { unevaluated: true });
        if (bodyP.startsWith("__NABLA_ERR__")) return bodyP;
        const opd = { op: m[1] === "sum" ? "sum" : "product",
                      var: v, a: la2plain(lo), b: la2plain(hi) };
        if (bodyP.startsWith("__NABLA_OP__"))
          opd.body = JSON.parse(bodyP.slice(12));
        else
          opd.body = bodyP;
        const extraP = la2plain(rest.slice(gb.len), { unevaluated: true });
        if (extraP.startsWith("__NABLA_ERR__")) return extraP;
        if (extraP) {
          opd.extra = extraP.startsWith("__NABLA_OP__")
            ? JSON.parse(extraP.slice(12)) : extraP;
        }
        return "__NABLA_OP__" + JSON.stringify(opd);
      }
    }

    /* ada kata kunci operator tapi GAK match format mana pun (mis.
       \sum_{n=} setengah diisi) -> sentinel pesan bersih, bukan dump
       sympify mentah */
    if (/\\(sum|prod|lim)(?![a-zA-Z])/.test(s))
      return "__NABLA_ERR__:int_malformed";
    return s;
  }

  function la2plain(la, opts) {
    const uneval = !!(opts && opts.unevaluated);
    let s = String(la || "").trim();
    if (!s) return "";
    try { s = cleanLatex(s); } catch (e) { /* cleanLatex tak ada? lanjut */ }
    /* prime: y^{\'\'} -> y^'' ( backend ODE paham y'' ).
       MathLive serialisasi tanda petik dua sebagai \doubleprime */
    s = s.replace(/\\prime/g, "'");
    s = s.replace(/\\doubleprime/g, "''");
    s = s.replace(/\^\{(''+)\}/g, "$1");
    /* notasi Leibniz utk ODE: \frac{dy}{dx} -> y', \frac{d^2 y}{dx^2} ->
       y'' (SEBELUM aturan \frac umum yang mengubahnya jadi simbol d/dx) */
    s = s.replace(/\\frac\s*\{\s*d\s*y\s*(?:\^\s*\{?\s*(\d+)\s*\}?)?\s*\}\s*\{\s*d\s*x\s*(?:\^\s*\{?\s*(\d+)\s*\}?)?\s*\}/g,
      (m, n1, n2) => {
        const ord = Math.max(parseInt(n1 || "0", 10), parseInt(n2 || "0", 10), 1);
        return "y" + "'".repeat(ord);
      });
    /* operator kalkulus (\int \sum \lim \frac{d}{dx}) → JSON op_data
       terstruktur, SEBELUM aturan lain biar body-nya utuh */
    s = calculus2sympy(s, uneval);
    if (s.startsWith("__NABLA_OP__") || s.startsWith("__NABLA_ERR__"))
      return s;   /* op terstruktur / sentinel: ATURAN LANJUTAN di-skip */

    /* perkalian implisit sebelum makro: k\pi → k*pi, x\arctan → x*arctan
       (dulu "kpi"/"xarctan" jadi SATU simbol = salah) */
    s = s.replace(/([0-9a-zA-Z])(?=\\[a-zA-Z])/g, "$1*");

    /* Ulang aturan pakai kurung seimbang s.d. habis (maks 8 putaran) */
    for (let pass = 0; pass < 8; pass++) {
      const before = s;
      /* normalizer fungsi berpangkat (K1): \sin^2x → (sin(x))^{2},
         \sin^{-1}x → asin(x), \sin 2x → sin(2x) — SEBELUM aturan lain */
      s = normalizeFnPowers(s);
      /* nama inverse arcsin-style → asin-style (sympify paham asin,
         gak paham arcsin) */
      s = s.replace(/\\arcsin/g, "asin").replace(/\\arccos/g, "acos")
           .replace(/\\arctan/g, "atan").replace(/\\arccot/g, "acot")
           .replace(/\\arcsec/g, "asec").replace(/\\arccsc/g, "acsc");
      /* \frac{a}{b} & \dfrac / \tfrac */
      s = s.replace(/\\(?:dfrac|tfrac|cfrac)?frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g,
        "($1)/($2)");
      /* \sqrt[n]{x} dan \sqrt{x} */
      s = s.replace(/\\sqrt\[([^\]]+)\]\{((?:[^{}]|\{[^{}]*\})*)\}/g,
        "(($2)**(1/($1)))");
      s = s.replace(/\\sqrt\{((?:[^{}]|\{[^{}]*\})*)\}/g, "sqrt($1)");
      /* \sin^{2}(x)/\ln^{2}(x) → (sin(x))**(2) (referensi latex_to_raw vc) */
      s = s.replace(/\\?(sin|cos|tan|sec|csc|cot|sinh|cosh|tanh|ln|log)\^\{(-?[0-9]+)\}\s*(\((?:[^()]|\([^()]*\))*\)|[a-z])(?!\\?\^\{-?[0-9]+\})/g,
        "($1($3))**($2)");
      /* e^{...} -> exp(...) (hanya e berdiri sendiri); e^x tanpa kurung */
      s = s.replace(/(^|[^a-zA-Z0-9_])e\^\{([^{}]*)\}/g, "$1exp($2)");
      s = s.replace(/(^|[^a-zA-Z0-9_])e\^\s*([a-zA-Z0-9.]+)/g, "$1exp($2)");
      /* \log_{b}(x) / \log_{b} x -> log(x)/log(b) (base bebas) */
      s = s.replace(/\\log_\{([^{}]*)\}\s*\(([^()]*)\)/g, "(log($2)/log($1))");
      s = s.replace(/\\log_\{([^{}]*)\}\s*([A-Za-z0-9.]+)/g, "(log($2)/log($1))");
      /* \binom{n}{k} -> binomial(n,k) */
      s = s.replace(/\\binom\{([^{}]*)\}\{([^{}]*)\}/g, "binomial($1,$2)");
      /* |x| / \left|x\right| -> abs(x) (sympy paham abs->Abs, mathjs
         engine grafik juga paham abs) */
      s = s.replace(/\|([^|]+)\|/g, "abs($1)");
      /* ^{...} -> ^(...) ; \cdot \times \div */
      s = s.replace(/\^\{([^{}]*)\}/g, "^($1)");
      s = s.replace(/\\(cdot|times)/g, "*").replace(/\\div/g, "/");
      /* \left \right \! dsb dekorasi */
      s = s.replace(/\\(?:left|right|[!,;:])/g, "");
      /* fungsi bernama */
      s = s.replace(/\\(sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan|arccot|asin|acos|atan|asec|acsc|acot|asinh|acosh|atanh|ln|log|exp|min|max|cbrt)\b/g, "$1");
      /* "2 ln 4" → "2*ln(4)": angka menempel sebelum nama fungsi
         (dengan ATAU tanpa spasi: e^{2\ln 4} → exp(2*ln(4))) */
      s = s.replace(/(\d)\s+(?=(?:arcsin|arccos|arctan|arccot|sin|cos|tan|cot|sec|csc|ln|log|exp|sqrt|cbrt|pi|theta|alpha|beta|gamma|mu|rho|lambda|phi|omega|epsilon|varepsilon|delta|sigma|tau|eta)\b)/g, "$1*");
      s = s.replace(/(\d)((?:arcsin|arccos|arctan|arccot|sin|cos|tan|cot|sec|csc|ln|log|exp|sqrt|cbrt)\b)/g, "$1*$2");
      /* "ln 4" → "ln(4)": satu token berikut jadi argumen */
      s = s.replace(/\b(arcsin|arccos|arctan|arccot|sin|cos|tan|cot|sec|csc|ln|log|exp|cbrt|sqrt)\s+([A-Za-z0-9.]+)/g, "$1($2)");
      /* \text{...} -> isinya */
      s = s.replace(/\\(?:text|mathrm|mathbf|operatorname)\{([^{}]*)\}/g, "$1");
      /* huruf yunani */
      s = s.replace(/\\(pi|theta|alpha|beta|gamma|mu|rho|lambda|phi|varphi|omega|epsilon|varepsilon|delta|sigma|tau|eta)/g, "$1");
      if (s === before) break;
    }

    /* makro sisa apa pun: buang */
    s = s.replace(/\\[a-zA-Z]+/g, "");

    /* perkalian implisit ala manusia → sympy/mathjs paham */
    s = s.replace(/(\d)\s*x/g, "$1*x");
    /* angka menempel huruf: x^2e^x → x^2*e^x, n2^n → n*2^n */
    s = s.replace(/([a-zA-Z])(?=[0-9])/g, "$1*");
    s = s.replace(/(\d)(?=[a-zA-Z])/g, "$1*");
    /* variabel satu huruf sebelum kurung: n(n+1) → n*(n+1) */
    s = s.replace(/(^|[^a-zA-Z0-9_])([a-df-z])(?![a-zA-Z0-9_])\s*\(/g, "$1$2*(");
    /* ")(huruf" / ")((" / ") huruf" → perkalian: \sin(x)\cos(2y) →
       sin(x)*cos(2y) (dulu cuma var x) */
    s = s.replace(/\)\s*(?=[a-zA-Z(])/g, ")*");
    s = s.replace(/(^|[^a-z0-9_])x\s*\(/g, "$1x*(");
    /* huruf menempel e^: xe^x → x*e^x (e = Euler) */
    s = s.replace(/([0-9a-zA-Z])e\^/g, "$1*e^");
    /* e berdiri sendiri (sudah tersisa) = exp(1) */
    s = s.replace(/(^|[^a-zA-Z0-9_])e(?![a-zA-Z0-9_])/g, "$1exp(1)");
    /* spasi antar nama fungsi dan buka-kurung: "sin (" → "sin(" */
    s = s.replace(/([a-zA-Z0-9)\]])\s+\(/g, "$1(");
    /* perkalian implisit via spasi: "x^2 y" → "x^2*y", "x exp(x)" →
       "x*exp(x)" (greek multi-huruf di-exclude biar "x theta" gak
       kepecah jadi "x*t heta") */
    s = s.replace(/([0-9a-zA-Z\)])\s+(?!(?:theta|alpha|beta|gamma|mu|lambda|omega|phi|varphi|sigma|delta|eta|rho|epsilon|tau|pi|oo)\b)([a-zA-Z0-9\(])/g, "$1*$2");

    return s.trim();
  }

  /* ---------- registry 20 tools ----------
     inputs: {id, label (kunci i18n), fb (fallback), type, ph, pre, plain,
              showIf, min/max utk select}
     type "mf" = field MathLive (LaTeX). "use" = contoh penggunaan (KaTeX). */
  const TOOLS = {
    integral: {
      wide: true,
      labels: { sym: "", num: "tools.lbl_num", dxn: "tools.integral.dn",
                dval: "tools.integral.dval", sumv: "tools.integral.sv",
                prodv: "tools.integral.pv", det: "tools.integral.det" },
      inputs: [
        { id: "expr", label: "tools.expr_fx", fb: "Fungsi f(x)", type: "mf", pre: "sin(x)/x" },
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["auto", "tools.integral.auto", "Auto (Deteksi Otomatis)"],
          ["def", "tools.integral.def", "Integral Tentu"],
          ["indef", "tools.integral.indef", "Integral Tak Tentu"],
          ["lim", "tools.integral.lim", "Limit"],
          ["diff", "tools.integral.diff", "Turunan (d/dx)"],
          ["sum", "tools.integral.sum", "Jumlah Deret (\u03a3)"],
          ["prod", "tools.integral.prod", "Perkalian Deret (\u220f)"],
          ["exp", "tools.integral.exp", "Eksponensial & Log"],
        ] },
        { id: "a", label: "tools.integral.a", fb: "Batas bawah a", ph: "0", def: "0", showIf: { mode: ["def", "sum", "prod"] } },
        { id: "b", label: "tools.integral.b", fb: "Batas atas b", ph: "3", def: "3", showIf: { mode: ["def", "sum", "prod"] } },
        { id: "x0", label: "tools.integral.x0lbl", fb: "Titik didekati x\u2080", ph: "0", showIf: { mode: ["lim"] } },
        { id: "n", label: "tools.integral.n", fb: "Orde turunan n (1-12)", ph: "1", showIf: { mode: ["diff"] } },
        { id: "xo", label: "tools.integral.xo", fb: "Titik evaluasi x (opsional)", ph: "2", showIf: { mode: ["diff"] } },
      ],
      use: [
        "\\displaystyle\\int_0^{3}\\frac{\\sin x}{x}\\,dx \\approx 1.84865",
        "\\dfrac{d}{dx}\\,x^{3} = 3x^{2},\\quad \\left.\\dfrac{d}{dx}x^{3}\\right|_{x=2} = 12",
        "\\sum_{x=1}^{5}x^{2} = 55",
        "\\displaystyle\\int x^2\\,dx = \\tfrac{x^3}{3} + C",
        "e^{2\\ln 4} = 16",
        "\\displaystyle\\lim_{x\\to 0}\\frac{\\sin x}{x} = 1",
      ],
    },
    matrix: {
      labels: { R: "" },
      matrixIn: true,
      inputs: [
        { id: "matrix", label: "tools.matrix.in", fb: "Matriks", type: "mf",
          pre: "\\begin{pmatrix}1 & 2 \\\\ 3 & 4\\end{pmatrix}" },
        { id: "op", label: "tools.op", fb: "Operasi", type: "select", opts: [
          ["det", "tools.matrix.det", "Determinan"],
          ["inv", "tools.matrix.inv", "Invers"],
          ["rank", "tools.matrix.rank", "Rank"],
          ["eig", "tools.matrix.eig", "Nilai & Vektor Eigen"],
          ["rref", "tools.matrix.rref", "Bentuk Eselon Baris"],
          ["T", "tools.matrix.transpose", "Transpos"],
        ] },
      ],
      hint: "tools.matrix.hint",
      use: [
        "\\det\\begin{pmatrix}1&2\\\\3&4\\end{pmatrix} = -2",
        "\\operatorname{rank}\\begin{pmatrix}1&1\\\\1&1\\end{pmatrix} = 1",
        "\\lambda\\,\\mathbf{v} = A\\,\\mathbf{v} \\;\\Rightarrow\\; \\begin{pmatrix}1&2\\\\3&4\\end{pmatrix},\\ \\lambda=-0.372,\\ 5.372",
      ],
    },
    ode: {
      labels: { y: "" },
      inputs: [
        { id: "eq", label: "tools.ode.eq", fb: "Persamaan diferensial", type: "mf", pre: "y'' + y = sin(x)" },
        { id: "ics", label: "tools.ode.ic", fb: "Syarat awal (opsional)", ph: "y(0) = 1, y'(0) = 0" },
      ],
      hint: "tools.ode.hint",
      use: [
        "y'' + y = \\sin(x),\\quad y(0)=1,\\ y'(0)=0",
        "y' = x \\Rightarrow y = \\tfrac{x^2}{2} + C",
        "\\text{ode eksponensial:}\\; y' = -2y \\Rightarrow y = Ce^{-2x}",
      ],
    },
    stats: {
      noRows: true,
      inputs: [
        { id: "data", label: "tools.stats.data", fb: "Data (angka, pisah dengan koma/spasi)", type: "textarea", ph: "2, 4, 4, 5, 7" },
      ],
      labels2: {
        n: "tools.stats.n", mean: "tools.stats.mean", median: "tools.stats.median",
        mode: "tools.stats.mode", min: "tools.stats.min", max: "tools.stats.max",
        sum: "tools.stats.sum", var_s: "tools.stats.var", std_s: "tools.stats.std",
      },
      use: [
        "\\text{data: } 2,\\,4,\\,4,\\,5,\\,7 \\Rightarrow \\bar{x} = 4.4,\\ \\sigma_s \\approx 1.8166",
        "\\tilde{x} = \\text{median} = 4",
      ],
    },
    thermo: {
      labels: { P: "tools.thermo.p", V: "tools.thermo.v", N: "tools.thermo.n", T: "tools.thermo.t",
                eta: "tools.thermo.eta", eta_pct: "tools.thermo.eta" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["ideal", "tools.thermo.ideal", "Hukum Gas Ideal (PV = nRT)"],
          ["carnot", "tools.thermo.carnot", "Efisiensi Carnot"],
        ] },
        { id: "solve", label: "tools.thermo.solve", fb: "Variabel yang dicari", type: "select", opts: [
          ["P", "tools.thermo.p", "Tekanan P (Pa)"],
          ["V", "tools.thermo.v", "Volume V (m\u00b3)"],
          ["N", "tools.thermo.n", "Jumlah mol n"],
          ["T", "tools.thermo.t", "Suhu T (K)"],
        ], showIf: { mode: ["ideal"] } },
        { id: "p", label: "tools.thermo.p", fb: "Tekanan P (Pa)", showIf: { mode: ["ideal"] } },
        { id: "v", label: "tools.thermo.v", fb: "Volume V (m\u00b3)", showIf: { mode: ["ideal"] } },
        { id: "n", label: "tools.thermo.n", fb: "Jumlah mol n", showIf: { mode: ["ideal"] } },
        { id: "t", label: "tools.thermo.t", fb: "Suhu T (K)", showIf: { mode: ["ideal"] } },
        { id: "thot", label: "tools.thermo.thot", fb: "Suhu panas T\u2103 (K)", ph: "600", showIf: { mode: ["carnot"] } },
        { id: "tcold", label: "tools.thermo.tcold", fb: "Suhu dingin (K)", ph: "400", showIf: { mode: ["carnot"] } },
      ],
      use: [
        "P\\,V = n\\,R\\,T \\;\\Rightarrow\\; V = \\dfrac{nRT}{P}",
        "\\eta_{\\text{Carnot}} = 1 - \\dfrac{T_c}{T_h} = 1 - \\dfrac{400}{600} \\approx 33.3\\%",
      ],
    },
    qm: {
      labels: { lambda: "tools.quantum.wl", E_J: "tools.quantum.ej", E_eV: "tools.quantum.eev",
                KE_J: "tools.quantum.kej", KE_eV: "tools.quantum.kev" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["debr", "tools.quantum.debr", "Panjang Gelombang de Broglie"],
          ["photon", "tools.quantum.photon", "Energi Foton"],
          ["photo", "tools.quantum.photo", "Efek Fotolistrik"],
        ] },
        { id: "mass", label: "tools.quantum.mass", fb: "Massa m (kg)", ph: "9.11e-31", showIf: { mode: ["debr"] } },
        { id: "vel", label: "tools.quantum.vel", fb: "Kecepatan v (m/s)", ph: "1e6", showIf: { mode: ["debr"] } },
        { id: "freq", label: "tools.quantum.freq", fb: "Frekuensi f (Hz)", ph: "1e15",
          showIf: { mode: ["photon", "photo"] } },
        { id: "work", label: "tools.quantum.work", fb: "Fungsi kerja \u03c6 (eV)", ph: "2",
          showIf: { mode: ["photo"] } },
      ],
      use: [
        "\\lambda_{\\text{de Broglie}} = \\dfrac{h}{m\\,v}",
        "E = h\\,f = \\dfrac{h\\,c}{\\lambda}",
        "K\\!E_{\\max} = h f - \\varphi",
      ],
    },
    es: {
      labels: { F: "tools.es.f", E: "tools.es.e", C: "tools.es.c" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["coulomb", "tools.es.coulomb", "Gaya Coulomb"],
          ["field", "tools.es.field", "Medan Muatan Titik"],
          ["cap", "tools.es.cap", "Kapasitor Datar"],
        ] },
        { id: "q1", label: "tools.es.q1", fb: "Muatan q\u2081 (C)", ph: "1e-6",
          showIf: { mode: ["coulomb", "field"] } },
        { id: "q2", label: "tools.es.q2", fb: "Muatan q\u2082 (C)", ph: "1e-6", showIf: { mode: ["coulomb"] } },
        { id: "r", label: "tools.es.r", fb: "Jarak r (m)", ph: "0.5", showIf: { mode: ["coulomb", "field"] } },
        { id: "a", label: "tools.es.a", fb: "Luas bidang A (m\u00b2)", ph: "0.01", showIf: { mode: ["cap"] } },
        { id: "d", label: "tools.es.d", fb: "Jarak antar plat d (m)", ph: "0.001", showIf: { mode: ["cap"] } },
      ],
      use: [
        "F = k_e\\,\\dfrac{q_1 q_2}{r^{2}}",
        "E = \\dfrac{k_e\\,q}{r^{2}}",
        "C = \\varepsilon_0\\,\\dfrac{A}{d}",
      ],
    },
    rel: {
      labels: { gamma: "tools.rel.gamma", dt: "tools.rel.dt", L: "tools.rel.l",
                E: "tools.rel.e", E0: "tools.rel.e0", K: "tools.rel.k" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["gamma", "tools.rel.gamma", "Faktor Lorentz \u03b3"],
          ["dilation", "tools.rel.dilation", "Dilatasi Waktu"],
          ["contraction", "tools.rel.contraction", "Kontraksi Panjang"],
          ["energy", "tools.rel.energy", "Energi Relativistik"],
        ] },
        { id: "v", label: "tools.rel.v", fb: "Kecepatan v (fraksi dari c)", ph: "0.5" },
        { id: "t0", label: "tools.rel.t0", fb: "Waktu diam t\u2080 (s)", ph: "10", showIf: { mode: ["dilation"] } },
        { id: "l0", label: "tools.rel.l0", fb: "Panjang diam L\u2080 (m)", ph: "100", showIf: { mode: ["contraction"] } },
        { id: "m", label: "tools.rel.m", fb: "Massa diam m (kg)", ph: "1", showIf: { mode: ["energy"] } },
      ],
      use: [
        "\\gamma = \\dfrac{1}{\\sqrt{1 - v^{2}/c^{2}}},\\quad v = 0.5c \\Rightarrow \\gamma \\approx 1.1547",
        "\\Delta t = \\gamma\\,\\Delta t_0,\\qquad L = \\dfrac{L_0}{\\gamma}",
        "E = \\gamma m_{0}c^{2},\\quad K = (\\gamma - 1)m_{0}c^{2}",
      ],
    },
    proj: {
      labels: { x_max: "tools.proj.range", y_max: "tools.proj.hmax", t: "tools.proj.tof" },
      inputs: [
        { id: "v0", label: "tools.proj.v0", fb: "Kecepatan awal v\u2080 (m/s)", ph: "20" },
        { id: "angle", label: "tools.proj.angle", fb: "Sudut elevasi (derajat)", ph: "45" },
        { id: "h0", label: "tools.proj.h0", fb: "Ketinggian awal (m)", ph: "0" },
        { id: "g", label: "tools.proj.g", fb: "Gravitasi g (m/s\u00b2)", ph: "9.81" },
      ],
      use: [
        "x_{\\max} = \\dfrac{v_0^{2}\\sin 2\\theta}{g}",
        "y_{\\max} = y_0 + \\dfrac{\\left(v_0\\sin\\theta\\right)^{2}}{2g}",
      ],
    },
    hydro: {
      labels: { P_gauge: "tools.hydro.pg", P_abs: "tools.hydro.pa", v2: "tools.hydro.v2" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["hstat", "tools.hydro.hstat", "Tekanan Hidrostatik"],
          ["cont", "tools.hydro.cont", "Persamaan Kontinuitas"],
          ["bern", "tools.hydro.bern", "Bernoulli (cari v\u2082)"],
        ] },
        { id: "rho", label: "tools.hydro.rho", fb: "Massa jenis \u03c1 (kg/m\u00b3)", ph: "1000",
          showIf: { mode: ["hstat", "bern"] } },
        { id: "h", label: "tools.hydro.h", fb: "Kedalaman h (m)", ph: "10", showIf: { mode: ["hstat"] } },
        { id: "a1", label: "tools.hydro.a1", fb: "Luas penampang A\u2081 (m\u00b2)", ph: "2", showIf: { mode: ["cont"] } },
        { id: "a2", label: "tools.hydro.a2", fb: "Luas penampang A\u2082 (m\u00b2)", ph: "1", showIf: { mode: ["cont"] } },
        { id: "v1", label: "tools.hydro.v1", fb: "Kecepatan v\u2081 (m/s)", ph: "3", showIf: { mode: ["cont", "bern"] } },
        { id: "p1", label: "tools.hydro.p1", fb: "Tekanan P\u2081 (Pa)", ph: "200000", showIf: { mode: ["bern"] } },
        { id: "p2", label: "tools.hydro.p2", fb: "Tekanan P\u2082 (Pa)", ph: "100000", showIf: { mode: ["bern"] } },
        { id: "h1", label: "tools.hydro.h1", fb: "Ketinggian h\u2081 (m)", ph: "0", showIf: { mode: ["bern"] } },
        { id: "h2", label: "tools.hydro.h2", fb: "Ketinggian h\u2082 (m)", ph: "0", showIf: { mode: ["bern"] } },
      ],
      use: [
        "P_{\\text{gauge}} = \\rho\\,g\\,h",
        "A_1 v_1 = A_2 v_2",
        "P_1 + \\tfrac{1}{2}\\rho v_1^{2} + \\rho g h_1 = P_2 + \\tfrac{1}{2}\\rho v_2^{2} + \\rho g h_2",
      ],
    },
    complex: {
      wide: true,
      labels: { abs: "tools.cplx.abs", arg_rad: "tools.cplx.argrad", arg_deg: "tools.cplx.argdeg",
                polar: "tools.cplx.polar", "z^n": "tools.cplx.zn", num: "tools.lbl_num" },
      inputs: [
        { id: "re", label: "tools.cplx.re", fb: "Bagian riil Re", ph: "1" },
        { id: "im", label: "tools.cplx.im", fb: "Bagian imajiner Im", ph: "1" },
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["polar", "tools.cplx.polar", "Bentuk Polar"],
          ["power", "tools.cplx.power", "Pangkat z\u207f"],
          ["roots", "tools.cplx.roots", "Akar ke-n"],
        ] },
        { id: "n", label: "tools.cplx.n", fb: "Pangkat / akar n", ph: "2", def: "2", showIf: { mode: ["power", "roots"] } },
      ],
      use: [
        "|z| = \\sqrt{a^{2}+b^{2}},\\qquad \\theta = \\arctan\\dfrac{b}{a}",
        "z = r\\,e^{i\\theta}",
        "z^{1/n} = \\sqrt[n]{r}\\,e^{\\,i(\\theta + 2\\pi k)/n}",
      ],
    },
    taylor: {
      labels: { poly: "" },
      inputs: [
        { id: "expr", label: "tools.expr_fx", fb: "Fungsi f(x)", type: "mf", pre: "exp(x)" },
        { id: "x0", label: "tools.taylor.x0", fb: "Titik pusat x\u2080", ph: "0", def: "0" },
        { id: "order", label: "tools.taylor.order", fb: "Orde (1-14)", ph: "4" },
      ],
      use: [
        "e^{x} \\approx 1 + x + \\dfrac{x^{2}}{2!} + \\dfrac{x^{3}}{3!}",
        "\\sin x \\approx x - \\dfrac{x^{3}}{3!} + \\dfrac{x^{5}}{5!}",
      ],
    },
    modmath: {
      labels: { res: "tools.mod.res", inv: "tools.mod.inv", check: "tools.mod.check",
                gcd: "tools.mod.gcd", lcm: "tools.mod.lcm", prime: "tools.mod.prime",
                factor: "tools.mod.factor" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["powmod", "tools.mod.powmod", "Perpangkatan Modular (a^b mod n)"],
          ["invmod", "tools.mod.invmod", "Invers Modular (a\u207b\u00b9 mod n)"],
          ["gcd", "tools.mod.gcdlcm", "GCD & LCM"],
          ["prime", "tools.mod.primefact", "Prima & Faktorisasi"],
        ] },
        { id: "a", label: "tools.mod.a", fb: "Bilangan a", ph: "2", def: "2" },
        { id: "b", label: "tools.mod.b", fb: "Bilangan b", ph: "10", def: "10", showIf: { mode: ["powmod"] } },
        { id: "b", label: "tools.mod.b", fb: "Bilangan b", ph: "18", def: "18", showIf: { mode: ["gcd"] } },
        { id: "n", label: "tools.mod.n", fb: "Modulus n", ph: "1000", def: "1000", showIf: { mode: ["powmod", "invmod"] } },
        { id: "n", label: "tools.mod.n", fb: "Bilangan n", ph: "360", def: "360", showIf: { mode: ["prime"] } },
      ],
      use: [
        "a^{b} \\bmod n:\\;\\; 2^{10} \\bmod 1000 = 24",
        "\\gcd(12,18) = 6,\\quad \\operatorname{lcm}(12,18) = 36",
        "97 \\text{ prima},\\;\\; 360 = 2^{3}\\cdot 3^{2}\\cdot 5",
      ],
    },
    entropy: {
      labels: { H: "tools.ent.h", H_max: "tools.ent.hmax", red: "tools.ent.red", k: "tools.stats.n" },
      inputs: [
        { id: "probs", label: "tools.ent.probs", fb: "Probabilitas (jumlah harus 1)", type: "textarea", ph: "0.5, 0.5" },
      ],
      use: [
        "H = -\\sum_{i} p_{i}\\,\\log_{2} p_{i}",
        "\\text{koin adil: } H = 1 \\text{ bit},\\quad H_{\\max} = \\log_{2} n",
      ],
    },
    poly: {
      wide: true,
      labels: { R: "" },
      inputs: [
        { id: "expr", label: "tools.poly.expr", fb: "Polinom p(x)", type: "mf", pre: "x^2 - 5x + 6" },
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["roots", "tools.poly.roots", "Akar-akar"],
          ["factor", "tools.poly.factor", "Faktorisasi"],
        ] },
      ],
      hint: "tools.poly.hint",
      use: [
        "p(x) = x^{2} - 5x + 6 \\;\\Rightarrow\\; x_{1}=2,\\ x_{2}=3",
        "x^{2} - 5x + 6 = (x-2)(x-3)",
        "\\text{derajat bawah 12, koefisien boleh pecahan}",
      ],
    },
    heatexp: {
      labels: { Q: "tools.heat.q", dir: "tools.heat.dir", dL: "tools.heat.dl" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["heat", "tools.heat.heat", "Kalor (Q = m c \u0394T)"],
          ["expand", "tools.heat.expand", "Pemuaian Linear"],
          ["latent", "tools.heat.latent", "Kalor Laten (Q = m L)"],
        ] },
        { id: "m", label: "tools.heat.m", fb: "Massa m (kg)", ph: "1", showIf: { mode: ["heat", "latent"] } },
        { id: "c", label: "tools.heat.c", fb: "Kalor jenis c (J/kg\u00b7K)", ph: "4186", showIf: { mode: ["heat"] } },
        { id: "t1", label: "tools.heat.t1", fb: "Suhu awal T\u2081 (\u00b0C)", ph: "20", showIf: { mode: ["heat"] } },
        { id: "t2", label: "tools.heat.t2", fb: "Suhu akhir T\u2082 (\u00b0C)", ph: "30", showIf: { mode: ["heat"] } },
        { id: "l0", label: "tools.heat.l0", fb: "Panjang awal L\u2080 (m)", ph: "10", showIf: { mode: ["expand"] } },
        { id: "alpha", label: "tools.heat.alpha", fb: "Koefisien \u03b1 (1/K)", ph: "1.2e-5", showIf: { mode: ["expand"] } },
        { id: "dt", label: "tools.heat.dt", fb: "Perubahan suhu \u0394T (K)", ph: "50", showIf: { mode: ["expand"] } },
        { id: "latent", label: "tools.heat.latentlbl", fb: "Kalor laten L (J/kg)", ph: "334000", showIf: { mode: ["latent"] } },
      ],
      use: [
        "Q = m\\,c\\,\\Delta T",
        "\\Delta L = \\alpha\\,L_0\\,\\Delta T",
        "Q = m\\,L \\;\\text{(fase ubah tanpa suhu naik)}",
      ],
    },
    schwartz: {
      labels: { rs: "tools.gr.rs", dil: "tools.gr.dil", dt_ratio: "tools.gr.dtratio",
                vesc: "tools.gr.vesc" },
      inputs: [
        { id: "msun", label: "tools.gr.msun", fb: "Massa M (Matahari)", ph: "1" },
        { id: "r", label: "tools.gr.r", fb: "Jarak r (m)", ph: "10000" },
      ],
      hint: "tools.gr.hint",
      use: [
        "r_s = \\dfrac{2GM}{c^{2}}",
        "\\left(1 - \\dfrac{r_s}{r}\\right)^{-1} \\;\\text{faktor perlambatan waktu}",
      ],
    },
    optics: {
      labels: { th2: "tools.opt.th2", crit: "tools.opt.crit", tir: "tools.opt.tir",
                di: "tools.opt.di", m: "tools.opt.m", kind: "tools.opt.kind", dy: "tools.opt.dy" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["snell", "tools.opt.snell", "Hukum Snell"],
          ["lens", "tools.opt.lens", "Lensa Tipis"],
          ["dslit", "tools.opt.dslit", "Celah Ganda"],
        ] },
        { id: "n1", label: "tools.opt.n1", fb: "Indeks n\u2081", ph: "1", showIf: { mode: ["snell"] } },
        { id: "n2", label: "tools.opt.n2", fb: "Indeks n\u2082", ph: "1.5", showIf: { mode: ["snell"] } },
        { id: "th1", label: "tools.opt.th1", fb: "Sudut datang \u03b8\u2081 (derajat)", ph: "30", showIf: { mode: ["snell"] } },
        { id: "f", label: "tools.opt.f", fb: "Fokus f (m)", ph: "0.1", showIf: { mode: ["lens"] } },
        { id: "do", label: "tools.opt.dobj", fb: "Jarak benda d\u2092 (m)", ph: "0.15", showIf: { mode: ["lens"] } },
        { id: "lam", label: "tools.opt.lam", fb: "Panjang gelombang \u03bb (m)", ph: "500e-9", showIf: { mode: ["dslit"] } },
        { id: "d", label: "tools.opt.d", fb: "Jarak celah d (m)", ph: "1e-4", showIf: { mode: ["dslit"] } },
        { id: "L", label: "tools.opt.L", fb: "Jarak layar L (m)", ph: "2", showIf: { mode: ["dslit"] } },
      ],
      use: [
        "n_1\\sin\\theta_1 = n_2\\sin\\theta_2",
        "\\dfrac{1}{f} = \\dfrac{1}{d_o} + \\dfrac{1}{d_i}",
        "d\\,\\sin\\theta = m\\,\\lambda \\;\\text{(interferensi maksimum)}",
      ],
    },
    shm: {
      labels: { T: "tools.shm.T", f: "tools.shm.f", omega: "tools.shm.omega", E: "tools.shm.E" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["mass", "tools.shm.mass", "Pegas (m, k)"],
          ["pend", "tools.shm.pend", "Bandul (L, g)"],
          ["energy", "tools.shm.energy", "Energi (A, k)"],
        ] },
        { id: "m", label: "tools.shm.m", fb: "Massa m (kg)", ph: "1", showIf: { mode: ["mass"] } },
        { id: "k", label: "tools.shm.k", fb: "Konstanta pegas k (N/m)", ph: "100", showIf: { mode: ["mass", "energy"] } },
        { id: "L", label: "tools.shm.L", fb: "Panjang tali L (m)", ph: "1", showIf: { mode: ["pend"] } },
        { id: "g", label: "tools.proj.g", fb: "Gravitasi g (m/s\u00b2)", ph: "9.81", showIf: { mode: ["pend"] } },
        { id: "A", label: "tools.shm.A", fb: "Amplitudo A (m)", ph: "0.1", showIf: { mode: ["energy"] } },
      ],
      use: [
        "T = 2\\pi\\sqrt{\\dfrac{m}{k}}",
        "T = 2\\pi\\sqrt{\\dfrac{L}{g}} \\;\\text{(bandul sederhana)}",
        "E_{\\text{energi}} = \\tfrac{1}{2}kA^{2}",
      ],
    },
    emind: {
      labels: { EMF: "tools.em.emf", V2: "tools.em.v2", kind: "tools.em.kind" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["faraday", "tools.em.faraday", "Faraday (EMF = N d\u03a6/dt)"],
          ["trafo", "tools.em.trafo", "Trafo Ideal"],
          ["motional", "tools.em.motional", "EMF Gerak (B v L)"],
        ] },
        { id: "N", label: "tools.em.n", fb: "Jumlah lilitan N", ph: "100", showIf: { mode: ["faraday"] } },
        { id: "dphi", label: "tools.em.dphi", fb: "Laju perubahan fluks d\u03a6/dt (Wb/s)", ph: "0.5", showIf: { mode: ["faraday"] } },
        { id: "v1", label: "tools.em.v1", fb: "Tegangan primer V\u2081 (V)", ph: "240", showIf: { mode: ["trafo"] } },
        { id: "n1", label: "tools.em.n1", fb: "Lilitan primer N\u2081", ph: "1000", showIf: { mode: ["trafo"] } },
        { id: "n2", label: "tools.em.n2", fb: "Lilitan sekunder N\u2082", ph: "100", showIf: { mode: ["trafo"] } },
        { id: "B", label: "tools.em.b", fb: "Medan magnet B (T)", ph: "0.5", showIf: { mode: ["motional"] } },
        { id: "v", label: "tools.em.v", fb: "Kecepatan v (m/s)", ph: "10", showIf: { mode: ["motional"] } },
        { id: "L", label: "tools.em.l", fb: "Panjang konduktor L (m)", ph: "0.2", showIf: { mode: ["motional"] } },
      ],
      use: [
        "\\varepsilon = N\\,\\dfrac{d\\Phi}{dt}",
        "\\dfrac{V_1}{V_2} = \\dfrac{N_1}{N_2} \\;\\text{(trafo ideal)}",
        "\\varepsilon = B\\,v\\,L \\;\\text{(EMF gerak)}",
      ],
    },

    /* ========================================================
       SIMULASI ADVANCED (simlab.py via /api/lab), 10 buah.
       Semua hasil plot = multi-trace; label row = kunci i18n
       grup sims.* (atau simbol LaTeX yang language-neutral). */
    slogistic: {
      labels: { r: "r", x0: "sims.x0", x_final: "sims.lg_xfinal",
                x_star: "sims.lg_xstar", period: "sims.lg_period",
                lyap: "sims.lg_lyap", regime: "sims.lg_regime",
                map: "", note: "" },
      inputs: [
        { id: "mode", label: "tools.mode", fb: "Mode", type: "select", opts: [
          ["series", "sims.lg_series", "Sei Waktu"],
          ["cobweb", "sims.lg_cobweb", "Cobweb"],
          ["bifurcation", "sims.lg_bif", "Diagram Bifurkasi"],
        ] },
        { id: "r", label: "sims.lg_r", fb: "Laju pertumbuhan r", ph: "2.8", def: "2.8", showIf: { mode: ["series", "cobweb"] } },
        { id: "x0", label: "sims.lg_x0", fb: "Populasi awal x\u2080", ph: "0.2", def: "0.2", showIf: { mode: ["series", "cobweb"] } },
        { id: "n", label: "sims.steps", fb: "Jumlah iterasi n", ph: "200", def: "200",
          showIf: { mode: ["series", "cobweb"] } },
      ],
      hint: "sims.lg_hint",
      use: [
        "x_{k+1} = r\\,x_k(1-x_k),\\quad r = 2 \\Rightarrow x^{*} = \\tfrac{1}{2}",
        "r = 3.2 \\Rightarrow \\text{periode } 2,\\quad r > 3.5699 \\Rightarrow \\text{kacau}",
        "\\lambda = \\ln|r(1-2x)| > 0 \\Leftrightarrow \\text{kacau}",
      ],
    },
    slorenz: {
      labels: { sigma: "\u03c3", rho: "\u03c1", beta: "\u03b2",
                t_end: "sims.lz_tend", state_max: "sims.lz_smax",
                regime: "sims.lg_regime", fp: "" },
      inputs: [
        { id: "sigma", label: "sims.lz_sig", fb: "\u03c3 (bilangan Prandtl)", ph: "10", def: "10" },
        { id: "rho", label: "sims.lz_rho", fb: "\u03c1 (bilangan Rayleigh)", ph: "28", def: "28" },
        { id: "beta", label: "sims.lz_beta", fb: "\u03b2 (bentuk geometri)", ph: "2.6667", def: "2.6667" },
        { id: "dt", label: "sims.lz_dt", fb: "\u0394t (langkah waktu)", ph: "0.005", def: "0.005" },
        { id: "steps", label: "sims.steps", fb: "Jumlah langkah", ph: "20000", def: "20000" },
      ],
      hint: "sims.lz_hint",
      use: [
        "\\dot{x} = \\sigma(y-x),\\quad \\dot{y} = x(\\rho-z) - y,\\quad \\dot{z} = xy - \\beta z",
        "\\rho = 28 \\Rightarrow \\text{atraktor aneh},\\quad \\rho < 24.74 \\Rightarrow \\text{titik tetap}",
      ],
    },
    sfourier: {
      labels: { L: "L", N: "N", a0: "a\u2080/2", a1: "a\u2081", b1: "b\u2081",
                a2: "a\u2082", b2: "b\u2082", a3: "a\u2083", b3: "b\u2083", series: "" },
      inputs: [
        { id: "expr", label: "tools.expr_fx", fb: "Fungsi f(x)", type: "mf", pre: "x" },
        { id: "L", label: "sims.fo_L", fb: "Setengah interval L", ph: "3.141592653589793", def: "3.141592653589793" },
        { id: "N", label: "sims.fo_N", fb: "Jumlah suku N", ph: "12", def: "12" },
      ],
      hint: "sims.fo_hint",
      use: [
        "f(x) = x \\text{ di } [-\\pi,\\pi] \\Rightarrow b_n = \\dfrac{2(-1)^{n+1}}{n}",
        "x \\approx 2\\left(\\sin x - \\tfrac{\\sin 2x}{2} + \\tfrac{\\sin 3x}{3} - \\cdots\\right)",
      ],
    },
    smatrix: {
      labels: { det: "\\det", trace: "\\mathrm{tr}", lam: "\\lambda",
                area: "sims.mx_area", kind: "sims.mx_kind" },
      matrixIn: true,
      inputs: [
        { id: "matrix", label: "tools.matrix.in", fb: "Matriks", type: "mbuild",
          def: "1,0;0,1", build: { min: 2, max: 2 } },
      ],
      hint: "sims.mx_hint",
      use: [
        "\\begin{pmatrix}0&-1\\\\1&0\\end{pmatrix} = \\text{rotasi } 90^{\\circ},\\ \\det = 1",
        "\\det A = \\text{faktor skala luas},\\quad \\lambda = \\text{nilai eigen}",
      ],
    },
    swalk: {
      labels: { n: "sims.w_n", steps: "sims.w_steps", seed: "sims.w_seed",
                rms: "sims.w_rms", rms_theory: "sims.w_rmsth",
                mean_x: "\u27e8x\u27e9", mean_y: "\u27e8y\u27e9", max_r: "sims.w_maxr" },
      inputs: [
        { id: "n", label: "sims.w_n", fb: "Jumlah partikel", ph: "120", def: "120" },
        { id: "steps", label: "sims.w_steps", fb: "Jumlah langkah", ph: "1500", def: "1500" },
        { id: "seed", label: "sims.w_seed", fb: "Seed (reproduksibel)", ph: "42", def: "42" },
      ],
      hint: "sims.w_hint",
      use: [
        "\\langle r^{2} \\rangle = n\\,\\ell^{2} \\Rightarrow \\text{RMS} = \\ell\\sqrt{n}",
        "\\text{difiusi: } \\langle x^{2} \\rangle = 2Dt",
      ],
    },
    sdblpend: {
      labels: { E0: "E\u2080", E1: "E\u2081", drift: "sims.drift",
                flips: "sims.dp_flips", t_end: "sims.dp_tend" },
      inputs: [
        { id: "view", label: "tools.mode", fb: "Tampilan", type: "select", opts: [
          ["angles", "sims.dp_angles", "Sudut vs Waktu"],
          ["path", "sims.dp_path", "Lintasan Ujung"],
        ] },
        { id: "m1", label: "sims.dp_m1", fb: "Massa m\u2081 (kg)", ph: "1", def: "1" },
        { id: "m2", label: "sims.dp_m2", fb: "Massa m\u2082 (kg)", ph: "1", def: "1" },
        { id: "L1", label: "sims.dp_l1", fb: "Tali L\u2081 (m)", ph: "1", def: "1" },
        { id: "L2", label: "sims.dp_l2", fb: "Tali L\u2082 (m)", ph: "1", def: "1" },
        { id: "th1", label: "sims.dp_th1", fb: "Sudut awal \u03b8\u2081 (derajat)", ph: "120", def: "120" },
        { id: "th2", label: "sims.dp_th2", fb: "Sudut awal \u03b8\u2082 (derajat)", ph: "-30", def: "-30" },
        { id: "g", label: "tools.proj.g", fb: "Gravitasi g (m/s\u00b2)", ph: "9.81", def: "9.81" },
        { id: "t_end", label: "sims.dp_tend", fb: "Durasi t (s)", ph: "20", def: "20" },
      ],
      hint: "sims.dp_hint",
      use: [
        "\\ddot{\\theta}_1,\\ \\ddot{\\theta}_2 = \\text{RK4},\\quad \\Delta t = 0.002\\,\\text{s}",
        "\\dfrac{\\Delta E}{E} \\approx 10^{-7} \\;\\text{(konservasi)}",
      ],
    },
    sdrag: {
      labels: { k: "k", range_drag: "sims.dr_rng", range_vac: "sims.dr_rngv",
                ratio: "sims.dr_ratio", h_max: "tools.proj.hmax",
                t_flight: "tools.proj.tof" },
      inputs: [
        { id: "v0", label: "tools.proj.v0", fb: "Kecepatan awal v\u2080 (m/s)", ph: "30", def: "30" },
        { id: "angle", label: "tools.proj.angle", fb: "Sudut elevasi (derajat)", ph: "45", def: "45" },
        { id: "m", label: "tools.heat.m", fb: "Massa m (kg)", ph: "0.145", def: "0.145" },
        { id: "Cd", label: "sims.dr_cd", fb: "Koefisien drag C\u2091", ph: "0.47", def: "0.47" },
        { id: "rho", label: "tools.hydro.rho", fb: "Massa jenis udara \u03c1 (kg/m\u00b3)", ph: "1.225", def: "1.225" },
        { id: "A", label: "tools.es.a", fb: "Luas penampang A (m\u00b2)", ph: "0.00426", def: "0.00426" },
        { id: "g", label: "tools.proj.g", fb: "Gravitasi g (m/s\u00b2)", ph: "9.81", def: "9.81" },
      ],
      hint: "sims.dr_hint",
      use: [
        "F_d = \\tfrac{1}{2}\\rho C_d A\\,v^{2}",
        "x_{\\text{vakum}} = \\dfrac{v_0^{2}\\sin 2\\theta}{g}",
      ],
    },
    skepler: {
      labels: { a: "a", e: "e", r_per: "sims.ke_rper", r_ap: "sims.ke_rap",
                T_theory: "sims.ke_Tt", T_meas: "sims.ke_Tm",
                E: "E", drift: "sims.drift", visviva: "" },
      inputs: [
        { id: "a", label: "sims.ke_a", fb: "Sumbu semi-mayor a", ph: "1", def: "1" },
        { id: "e", label: "sims.ke_e", fb: "Eksentrisitas e (0-1)", ph: "0.5", def: "0.5" },
        { id: "mu", label: "sims.ke_mu", fb: "\u03bc = GM (konstanta gravitasi)", ph: "1", def: "1" },
        { id: "orbits", label: "sims.ke_orbits", fb: "Jumlah orbit", ph: "2", def: "2" },
      ],
      hint: "sims.ke_hint",
      use: [
        "T = 2\\pi\\sqrt{\\dfrac{a^{3}}{\\mu}} \\;\\text{(Hukum III Kepler)}",
        "v^{2} = \\mu\\left(\\dfrac{2}{r} - \\dfrac{1}{a}\\right) \\;\\text{(vis-viva)}",
      ],
    },
    sslit: {
      labels: { dy: "\\Delta y", formula: "", n_fringes: "sims.sl_nfr",
                y_env: "sims.sl_yenv", envmin: "" },
      inputs: [
        { id: "lam", label: "tools.opt.lam", fb: "Panjang gelombang \u03bb (m)", ph: "500e-9", def: "500e-9" },
        { id: "d", label: "tools.opt.d", fb: "Jarak celah d (m)", ph: "1e-4", def: "1e-4" },
        { id: "L", label: "tools.opt.L", fb: "Jarak layar L (m)", ph: "2", def: "2" },
        { id: "a", label: "sims.sl_a", fb: "Lebar celah a (m, 0 = ideal)", ph: "2.5e-5", def: "2.5e-5" },
        { id: "span", label: "sims.sl_span", fb: "Setengah rentang layar (\u00d7 \u0394y)", ph: "5", def: "5" },
      ],
      hint: "sims.sl_hint",
      use: [
        "I(y) = \\cos^{2}\\!\\left(\\dfrac{\\pi d y}{\\lambda L}\\right) \\cdot \\mathrm{sinc}^{2}\\!\\left(\\dfrac{\\pi a y}{\\lambda L}\\right)",
        "\\Delta y = \\dfrac{\\lambda L}{d}",
      ],
    },
    sschrod: {
      labels: { norm0: "\u2016\u03c8\u2016\u2080", normT: "\u2016\u03c8\u2016(t)",
                drift: "sims.drift", E: "E", v_theory: "sims.qm_vth",
                v_meas: "sims.qm_vm", R_prob: "sims.qm_R",
                T_prob: "sims.qm_T", units: "" },
      inputs: [
        { id: "k0", label: "sims.qm_k0", fb: "Bilangan gelombang k\u2080", ph: "1.5", def: "1.5" },
        { id: "x0", label: "sims.qm_x0", fb: "Posisi awal x\u2080", ph: "-40", def: "-40" },
        { id: "sigma", label: "sims.qm_sigma", fb: "Lebar paket \u03c3", ph: "4", def: "4" },
        { id: "V0", label: "sims.qm_V0", fb: "Tinggi barrier V\u2080 (0 = bebas)", ph: "0", def: "0" },
        { id: "w", label: "sims.qm_w", fb: "Lebar barrier w (0 = bebas)", ph: "0", def: "0" },
        { id: "steps", label: "sims.steps", fb: "Jumlah langkah", ph: "3000", def: "3000" },
      ],
      hint: "sims.qm_hint",
      use: [
        "i\\,\\dfrac{\\partial \\psi}{\\partial t} = -\\dfrac{1}{2}\\dfrac{\\partial^{2}\\psi}{\\partial x^{2}} + V(x)\\,\\psi",
        "\\hbar = m = 1,\\quad E = \\dfrac{k_0^{2}}{2},\\quad v = k_0",
      ],
    },

    /* ========================================================
       ADVANCED GRAPHERS (graphlab.py validasi, graphers.js render)
       Interaksi (pan/zoom/drag/slider) 100% client-side. */
    gdomain: {
      labels: { map: "" },
      inputs: [
        { id: "expr", label: "graph.expr_fz", fb: "Fungsi f(z)", type: "mf", pre: "1/z" },
        { id: "range", label: "graph.range", fb: "Rentang bidang", type: "range", min: 0.5, max: 20, step: 0.5, def: "4" },
        { id: "res", label: "graph.res", fb: "Resolusi", type: "range", min: 120, max: 720, step: 40, def: "480" },
        { id: "scheme", label: "graph.scheme", fb: "Skema warna", type: "select", opts: [
          ["hue", "graph.sch_hue", "Hue"],
          ["phase", "graph.sch_phase", "Phase"],
          ["stripes", "graph.sch_stripes", "Stripes"],
          ["shade", "graph.sch_shade", "Shade"],
        ] },
      ],
      hint: "graph.hint_gdomain",
      use: ["f(z) = \\dfrac{1}{z}", "f(z) = z^{3} - 1", "f(z) = \\exp\\left(\\tfrac{1}{z}\\right)"],
    },
    gfractal: {
      labels: { note: "", iter: "graph.iter" },
      inputs: [
        { id: "mode", label: "graph.mode", fb: "Mode", type: "select", opts: [
          ["mandelbrot", "graph.m_mand", "Mandelbrot"],
          ["julia", "graph.m_julia", "Julia"],
          ["newton", "graph.m_newton", "Newton"],
        ] },
        { id: "iter", label: "graph.iter", fb: "Iterasi", type: "range", min: 20, max: 500, step: 10, def: "150" },
        { id: "power", label: "graph.power", fb: "Pangkat z", type: "range", min: 2, max: 6, step: 1, def: "2",
          showIf: { mode: ["mandelbrot", "julia"] } },
        { id: "cre", label: "graph.cre", fb: "Re(c)", type: "range", min: -2, max: 2, step: 0.001, def: "-0.7269",
          showIf: { mode: ["julia"] } },
        { id: "cim", label: "graph.cim", fb: "Im(c)", type: "range", min: -2, max: 2, step: 0.001, def: "0.1889",
          showIf: { mode: ["julia"] } },
      ],
      hint: "graph.hint_gfractal",
      use: ["z_{n+1} = z_n^{2} + c", "c = -0.7269 + 0.1889i\\ \\text{(dendrite)}"],
    },
    gsurf3d: {
      labels: { note: "", n: "graph.n" },
      inputs: [
        { id: "expr", label: "graph.expr_fxy", fb: "Fungsi f(x,y)", type: "mf", pre: "sin(x)*cos(2*y)" },
        { id: "n", label: "graph.n", fb: "Resolusi grid", type: "range", min: 16, max: 60, step: 4, def: "40" },
        { id: "px", label: "graph.px", fb: "x\u2080 titik singgung", type: "range", min: -4, max: 4, step: 0.1, def: "1" },
        { id: "py", label: "graph.py", fb: "y\u2080 titik singgung", type: "range", min: -4, max: 4, step: 0.1, def: "1" },
        { id: "range", label: "graph.range", fb: "Rentang sumbu", type: "range", min: 1, max: 10, step: 0.5, def: "4" },
      ],
      hint: "graph.hint_gsurf3d",
      use: ["z = \\sin x\\,\\cos 2y", "\\text{bidang singgung: } z = f_0 + f_x\\Delta x + f_y\\Delta y"],
    },
    gfrenet: {
      labels: { note: "", n: "graph.n" },
      inputs: [
        { id: "xt", label: "graph.xt", fb: "x(t)", type: "mf", pre: "3*cos(t)" },
        { id: "yt", label: "graph.yt", fb: "y(t)", type: "mf", pre: "3*sin(t)" },
        { id: "zt", label: "graph.zt", fb: "z(t)", type: "mf", pre: "t/2" },
        { id: "tmax", label: "graph.tmax", fb: "t maksimum", type: "range", min: 1, max: 40, step: 0.5, def: "18" },
        { id: "t", label: "graph.t", fb: "titik frame t", type: "range", min: 0.01, max: 40, step: 0.01, def: "2" },
        { id: "n", label: "graph.n", fb: "Sampel kurva", type: "range", min: 50, max: 600, step: 25, def: "300" },
      ],
      hint: "graph.hint_gfrenet",
      use: ["\\mathbf{T} = \\dfrac{\\mathbf{r}'}{\\|\\mathbf{r}'\\|},\\quad \\mathbf{B} = \\mathbf{T}\\times\\mathbf{N}"],
    },
    gtrans3d: {
      labels: { det: "det", note: "", morph: "graph.morph" },
      matrixIn: true,
      inputs: [
        { id: "matrix", label: "tools.matrix.in", fb: "Matriks 3\u00d73", type: "mbuild",
          def: "1,0.5,0;0,1,0.3;0,0,1", build: { min: 3, max: 3 } },
        { id: "morph", label: "graph.morph", fb: "Morph I \u2192 A", type: "range", min: 0, max: 1, step: 0.01, def: "1" },
      ],
      hint: "graph.hint_gtrans3d",
      use: ["A\\mathbf{i},\\ A\\mathbf{j},\\ A\\mathbf{k} = \\text{kolom } A", "\\det A = \\text{faktor volume}"],
    },
    gslope: {
      labels: { note: "", density: "graph.density" },
      inputs: [
        { id: "expr", label: "graph.expr_fxy2", fb: "y' = f(x,y)", type: "mf", pre: "x - y" },
        { id: "density", label: "graph.density", fb: "Kerapatan field", type: "range", min: 8, max: 40, step: 2, def: "20" },
        { id: "xlo", label: "graph.xlo", fb: "x minimum", type: "range", min: -20, max: 0, step: 1, def: "-8" },
        { id: "xhi", label: "graph.xhi", fb: "x maksimum", type: "range", min: 0, max: 20, step: 1, def: "8" },
      ],
      hint: "graph.hint_gslope",
      use: ["y' = x - y", "\\text{klik canvas} \\Rightarrow \\text{solusi RK4}"],
    },
    gdist: {
      labels: { n: "graph.w_n2", mean: "graph.mean" },
      inputs: [
        { id: "dist", label: "graph.dist", fb: "Distribusi", type: "select", opts: [
          ["normal", "graph.d_normal", "Normal"],
          ["binomial", "graph.d_binom", "Binomial"],
          ["poisson", "graph.d_poisson", "Poisson"],
          ["exponential", "graph.d_expo", "Eksponensial"],
          ["uniform", "graph.d_uniform", "Uniform"],
        ] },
        { id: "mu", label: "graph.mu", fb: "\u03bc", type: "range", min: -10, max: 10, step: 0.1, def: "0",
          showIf: { dist: ["normal"] } },
        { id: "sd", label: "graph.sd", fb: "\u03c3", type: "range", min: 0.2, max: 5, step: 0.05, def: "1",
          showIf: { dist: ["normal"] } },
        { id: "n", label: "graph.w_n2", fb: "n", type: "range", min: 1, max: 100, step: 1, def: "10",
          showIf: { dist: ["binomial"] } },
        { id: "p", label: "graph.p", fb: "p", type: "range", min: 0, max: 1, step: 0.01, def: "0.5",
          showIf: { dist: ["binomial"] } },
        { id: "lam", label: "graph.lam", fb: "\u03bb", type: "range", min: 0.1, max: 20, step: 0.1, def: "2",
          showIf: { dist: ["poisson", "exponential"] } },
        { id: "lo", label: "graph.lo", fb: "batas bawah", type: "range", min: -20, max: 20, step: 1, def: "0",
          showIf: { dist: ["uniform"] } },
        { id: "hi", label: "graph.hi", fb: "batas atas", type: "range", min: -20, max: 40, step: 1, def: "10",
          showIf: { dist: ["uniform"] } },
        { id: "a", label: "graph.a", fb: "a (batas bawah P)", type: "range", min: -20, max: 100, step: 0.25, def: "-1" },
        { id: "b", label: "graph.b", fb: "b (batas atas P)", type: "range", min: -20, max: 100, step: 0.25, def: "1" },
      ],
      hint: "graph.hint_gdist",
      use: ["P(a \\le X \\le b) = \\text{area di bawah PDF}", "F(x) = P(X \\le x)"],
    },
    ggraphalgo: {
      labels: { note: "" },
      inputs: [
        { id: "algo", label: "graph.algo", fb: "Algoritma", type: "select", opts: [
          ["dijkstra", "graph.a_dijkstra", "Dijkstra"],
          ["bfs", "graph.a_bfs", "BFS"],
          ["dfs", "graph.a_dfs", "DFS"],
          ["kruskal", "graph.a_kruskal", "MST (Kruskal)"],
        ] },
        { id: "n", label: "graph.w_n2", fb: "Jumlah node", type: "range", min: 4, max: 26, step: 1, def: "12" },
        { id: "density", label: "graph.density2", fb: "Kepadatan edge", type: "range", min: 0.1, max: 0.9, step: 0.05, def: "0.35" },
        { id: "seed", label: "sims.w_seed", fb: "Seed", type: "range", min: 0, max: 999, step: 1, def: "42" },
      ],
      hint: "graph.hint_ggraphalgo",
      use: ["\\text{drag node} \\Leftrightarrow \\text{recompute}"],
    },
    gfield: {
      labels: { note: "", n: "graph.w_n2", equip: "graph.equip" },
      inputs: [
        { id: "n", label: "graph.w_n2", fb: "Jumlah muatan", type: "range", min: 1, max: 8, step: 1, def: "4" },
        { id: "equip", label: "graph.equip", fb: "Garis ekipotensial", type: "range", min: 0, max: 40, step: 2, def: "18" },
        { id: "seed", label: "sims.w_seed", fb: "Seed", type: "range", min: 0, max: 999, step: 1, def: "7" },
      ],
      hint: "graph.hint_gfield",
      use: ["\\mathbf{E} = \\sum_i \\dfrac{k q_i}{r_i^{2}}\\hat{\\mathbf{r}}_i", "\\text{drag muatan merah/biru!}"],
    },
    gpvcycle: {
      labels: { eta: "graph.eta", note: "", formula: "" },
      inputs: [
        { id: "cycle", label: "graph.cycle", fb: "Siklus", type: "select", opts: [
          ["carnot", "graph.c_carnot", "Carnot"],
          ["otto", "graph.c_otto", "Otto"],
          ["diesel", "graph.c_diesel", "Diesel"],
        ] },
        { id: "th", label: "graph.th", fb: "T panas (K)", type: "range", min: 100, max: 2000, step: 10, def: "600",
          showIf: { cycle: ["carnot"] } },
        { id: "tc", label: "graph.tc", fb: "T dingin (K)", type: "range", min: 50, max: 1000, step: 10, def: "300",
          showIf: { cycle: ["carnot"] } },
        { id: "r", label: "graph.r", fb: "Rasio kompresi r", type: "range", min: 1.5, max: 30, step: 0.5, def: "9",
          showIf: { cycle: ["otto", "diesel"] } },
        { id: "rc", label: "graph.rc", fb: "Cut-off rc", type: "range", min: 1.3, max: 7, step: 0.1, def: "2.5",
          showIf: { cycle: ["diesel"] } },
        { id: "gamma", label: "graph.gamma", fb: "\u03b3", type: "range", min: 1.05, max: 1.8, step: 0.01, def: "1.4",
          showIf: { cycle: ["otto", "diesel"] } },
      ],
      hint: "graph.hint_gpvcycle",
      use: ["\\eta_{\\text{Carnot}} = 1 - \\dfrac{T_c}{T_h}", "\\eta_{\\text{Otto}} = 1 - r^{1-\\gamma}"],
    },
    gising: {
      labels: { note: "", size: "graph.size", temp: "graph.temp", speed: "graph.speed" },
      inputs: [
        { id: "size", label: "graph.size", fb: "Ukuran lattice", type: "range", min: 16, max: 160, step: 8, def: "100" },
        { id: "temp", label: "graph.temp", fb: "Temperatur T", type: "range", min: 0.05, max: 8, step: 0.01, def: "2.269" },
        { id: "speed", label: "graph.speed", fb: "Kecepatan sweep", type: "range", min: 1, max: 60, step: 1, def: "30" },
      ],
      hint: "graph.hint_gising",
      use: ["H = -J\\sum_{\\langle i,j \\rangle} s_i s_j", "T_c \\approx 2.269\\ J"],
    },
    gminkowski: {
      labels: { gamma: "tools.rel.gamma" },
      inputs: [
        { id: "v", label: "graph.v", fb: "Kecepatan frame v/c", type: "range", min: 0, max: 0.99, step: 0.01, def: "0.5" },
      ],
      hint: "graph.hint_gminkowski",
      use: ["\\text{drag event} \\Rightarrow s^{2} = c^{2}t^{2} - x^{2}\\ \\text{invarian}"],
    },
    gfluid: {
      labels: { note: "", size: "graph.size", visc: "graph.visc", diff: "graph.diff" },
      inputs: [
        { id: "size", label: "graph.size", fb: "Resolusi grid", type: "range", min: 48, max: 192, step: 16, def: "128" },
        { id: "visc", label: "graph.visc", fb: "Viskositas", type: "range", min: 0, max: 0.000001, step: 0.0000001, def: "0.0000002" },
        { id: "diff", label: "graph.diff", fb: "Difusi tinta", type: "range", min: 0, max: 0.000001, step: 0.0000001, def: "0.00000005" },
      ],
      hint: "graph.hint_gfluid",
      use: ["\\text{drag di canvas} \\Rightarrow \\text{injeksi tinta + kecepatan}"],
    },
    ggeodesic: {
      labels: { photon_sphere: "graph.photon", rs: "graph.rs", fate: "graph.fate",
                note: "", formula: "" },
      inputs: [
        { id: "mode", label: "graph.mode", fb: "Mode", type: "select", opts: [
          ["light", "graph.g_light", "Foton (b)"],
          ["massive", "graph.g_massive", "Partikel (E, L)"],
        ] },
        { id: "b", label: "graph.b", fb: "Impact parameter b", type: "range", min: 1.05, max: 6, step: 0.01, def: "3",
          showIf: { mode: ["light"] } },
        { id: "E", label: "graph.E", fb: "Energi E/m", type: "range", min: 0.55, max: 2, step: 0.01, def: "0.95",
          showIf: { mode: ["massive"] } },
        { id: "L", label: "graph.L", fb: "L/m", type: "range", min: 0, max: 6, step: 0.01, def: "1.2",
          showIf: { mode: ["massive"] } },
      ],
      hint: "graph.hint_ggeodesic",
      use: ["\\dfrac{d^{2}u}{d\\varphi^{2}} = \\dfrac{3}{2}r_s u^{2} - u", "b < 1.5\\,r_s \\Rightarrow \\text{tertelan}"],
    },
    gray: {
      labels: { formula: "" },
      inputs: [
        { id: "f1", label: "graph.f1", fb: "Fokus lensa 1 f\u2081 (px)", type: "range", min: -300, max: 300, step: 5, def: "150" },
        { id: "f2", label: "graph.f2", fb: "Fokus lensa 2 f\u2082 (px)", type: "range", min: -300, max: 300, step: 5, def: "-150" },
        { id: "d12", label: "graph.d12", fb: "Jarak antar lensa", type: "range", min: 40, max: 800, step: 10, def: "320" },
        { id: "nray", label: "graph.nray", fb: "Jumlah sinar", type: "range", min: 3, max: 15, step: 1, def: "7" },
      ],
      hint: "graph.hint_gray",
      use: ["\\dfrac{1}{f} = \\dfrac{1}{d_o} + \\dfrac{1}{d_i}", "f_1 > 0\\ \\text{konveks},\\ f_2 < 0\\ \\text{konkaf}"],
    },
  };

  /* terjemahan nilai khusus (nilai verbal dari backend) */
  const VALUE_MAP = {
    tolak: "tools.es.repel", tarik: "tools.es.attract", nol: "tools.es.zero",
    serap: "tools.heat.dir_in", lepas: "tools.heat.dir_out",
    nyata: "tools.opt.real", maya: "tools.opt.virtual",
    ya: "tools.yes", bukan: "tools.no",
    /* nilai rezim/jenis dari simulasi (simlab.py) */
    punah: "sims.rg_punah", titik_tetap: "sims.rg_tetap",
    periodik: "sims.rg_periodik", kacau: "sims.rg_kacau",
    rotasi: "sims.kd_rotasi", refleksi: "sims.kd_refleksi",
    shear: "sims.kd_shear", skala: "sims.kd_skala", singular: "sims.kd_singular",
  };

  /* terjemahan baris "note" LaTeX dari backend (graphlab.py) — teks \text{}
     Indonesia di dalam formula dipetakan literal-persis ke key i18n grup
     graph.*, biar baris catatan ikut bahasa aktif. Tanpa key = teks asli. */
  const NOTE_KEYS = {
    "z = f(x,y)\\ +\\ \\text{bidang singgung di } (x_0, y_0)": "graph.note_gsurf3d",
    "\\mathbf{T}, \\mathbf{N}, \\mathbf{B} = \\text{frame Frenet},\\ \\kappa, \\tau \\text{ numerik}": "graph.note_gfrenet",
    "f(z) \\text{ di bidang kompleks},\\ \\mathrm{hue} = \\arg f,\\ \\mathrm{shade} = |f|": "graph.note_gdomain",
    "\\det A = \\text{faktor volume},\\ \\text{basis } \\mathbf{i},\\mathbf{j},\\mathbf{k} \\text{ ikut}": "graph.note_gtrans3d",
    "y' = f(x,y)\\ \\text{— klik titik awal untuk solusi RK4}": "graph.note_gslope",
    "\\text{drag node, pilih algoritma, lihat animasi langkah}": "graph.note_ggraphalgo",
    "\\mathbf{E} = \\sum_i \\dfrac{k q_i}{r_i^{2}}\\hat{r}_i\\ \\text{— drag muatan!}": "graph.note_gfield",
  };

  /* tool simulasi: contoh penggunaan di-resolve dr grup i18n sims.* */
  const SIM_IDS = new Set(["slogistic", "slorenz", "sfourier", "smatrix", "swalk",
    "sdblpend", "sdrag", "skepler", "sslit", "sschrod"]);

  let current = null;   // tool yang lagi dibuka
  let currentId = "";
  let lastErrJ = null;   // error API terakhir (utk re-translate saat ganti bahasa)
  let lastData = null;  // hasil terakhir (buat re-render saat ganti bahasa)
  let currentEngine = "";  // engine grapher aktif
  let lastEngineParams = null;

  /* ---------- matrix builder (mbuild) ----------
     Grid sel klik-ketik ala mathway: +/− baris & kolom, sel angka.
     Nilai dikomposisi ke input hidden "r,c;r,c" (backend tetap sama),
     event 'input' di-dispatch biar preview KaTeX matrixIn ikut update. */
  function initMxBuild(wrap, hidden, min, max) {
    let state;
    try {
      state = String(hidden.value || "").split(";").filter(Boolean).map((r) =>
        (r.match(/[^,\s]+/g) || ["0"]).map((v) => {
          const f = parseFloat(v);
          return isNaN(f) ? 0 : f;
        }));
    } catch (e) { state = null; }
    if (!state || !state.length) state = [[0, 0], [0, 0]];

    function clamp() {
      while (state.length < min) state.push(state[0] ? state[0].map(() => 0) : [0]);
      while (state.length > max) state.pop();
      const w = Math.min(max, Math.max(min, Math.max(...state.map((r) => r.length))));
      state.forEach((r) => {
        while (r.length < w) r.push(0);
        while (r.length > w) r.pop();
      });
    }

    function compose(rerender) {
      clamp();
      hidden.value = state.map((r) => r.join(",")).join(";");
      hidden.dispatchEvent(new Event("input", { bubbles: true }));
      if (rerender) render();
    }

    function render() {
      const tAdd = (k, fb) => (window.I18N ? I18N.t(k, fb) : fb);
      let html = '<div class="mx-rows">';
      state.forEach((row, ri) => {
        html += '<div class="mx-row">' + row.map((v, ci) =>
          `<input class="mx-cell" data-r="${ri}" data-c="${ci}" ` +
          `value="${v}" inputmode="decimal" autocomplete="off">`).join("") + "</div>";
      });
      html += "</div>";
      /* tombol +/- baris/kolom HANYA untuk builder berukuran variabel.
         Untuk tool dgn matriks terkunci (gtrans3d = 3x3, smatrix = 2x2),
         min === max => semua tombol no-op permanen (ukuran disyaratkan
         matematika/backend) — sembunyikan daripada jadi jebakan klik. */
      if (min !== max) {
        html += `<div class="mx-btns">` +
          `<button type="button" class="mx-btn" data-act="addrow">＋ ${escHtml(tAdd("tools.mtx_addrow", "Tambah baris"))}</button>` +
          `<button type="button" class="mx-btn" data-act="delrow">− ${escHtml(tAdd("tools.mtx_delrow", "Hapus baris"))}</button>` +
          `<button type="button" class="mx-btn" data-act="addcol">＋ ${escHtml(tAdd("tools.mtx_addcol", "Tambah kolom"))}</button>` +
          `<button type="button" class="mx-btn" data-act="delcol">− ${escHtml(tAdd("tools.mtx_delcol", "Hapus kolom"))}</button>` +
          `</div>`;
      }
      wrap.innerHTML = html;
    }

    wrap.addEventListener("click", (e) => {
      const btn = e.target.closest(".mx-btn");
      if (!btn) return;
      const act = btn.dataset.act;
      if (act === "addrow" && state.length < max) state.push(new Array(state[0].length).fill(0));
      if (act === "delrow" && state.length > min) state.pop();
      if (act === "addcol" && state[0].length < max) state.forEach((r) => r.push(0));
      if (act === "delcol" && state[0].length > min) state.forEach((r) => r.pop());
      compose(true);
    });
    wrap.addEventListener("input", (e) => {
      const cell = e.target.closest(".mx-cell");
      if (!cell) return;
      const f = parseFloat(cell.value.replace(",", "."));
      state[+cell.dataset.r][+cell.dataset.c] = isNaN(f) ? 0 : f;
      // update hidden TANPA re-render, jangan hilangkan fokus ketik
      hidden.value = state.map((r) => r.join(",")).join(";");
      hidden.dispatchEvent(new Event("input", { bubbles: true }));
    });

    compose(true);
  }

  /* ---------- render form ---------- */
  function visible(inp, values) {
    if (!inp.showIf) return true;
    return Object.entries(inp.showIf).every(([k, list]) => list.includes(values[k]));
  }

  /* deteksi operator di mathfield tool integral (op_data / null) */
  function integralDetectedOp() {
    if (currentId !== "integral") return null;
    const mf = $("ti_expr");
    if (!mf) return null;
    const raw = (mf.getValue ? mf.getValue() : mf.value) || "";
    try {
      const out = la2plain(raw, { unevaluated: true });
      if (out.startsWith("__NABLA_OP__")) return JSON.parse(out.slice(12));
    } catch (e) { /* belum parse-able */ }
    return null;
  }
  /* op_data -> mode ekvivalen (utk visibilitas field & auto-switch) */
  function opModeOf(opd) {
    if (!opd) return null;
    return { integral: opd.has_bounds ? "def" : "indef",
             limit: "lim", derivative: "diff", subs_deriv: "diff",
             sum: "sum", product: "prod" }[opd.op] || null;
  }

  function bacaNilai(el, type) {
    /* nilai siap-backend dari elemen (mf = LaTeX dikonversi, lain apa adanya).
       Field expr tool integral: operator kalkulus di input dikirim sebagai
       objek TAK-EVALUASI (Integral/Sum/..) -> backend terapkan SEKALI. */
    let raw;
    if (type === "mf") raw = el.getValue ? el.getValue() : el.value;
    else raw = el.value;
    raw = (raw || "").trim();
    if (type === "mf") {
      /* tool matrix: LaTeX mentah (pmatrix) diteruskan apa adanya —
         backend yang parse \begin{pmatrix} NxN apa pun */
      if (currentId === "matrix") return raw;
      const uneval = currentId === "integral" && el.id === "ti_expr";
      return la2plain(raw, { unevaluated: uneval });
    }
    return raw;
  }

  function collect() {
    const vals = {};
    if (!current) return vals;
    current.inputs.forEach((inp) => {
      const el = $("ti_" + inp.id);
      if (el) vals[inp.id] = bacaNilai(el, inp.type);
      else if (vals[inp.id] === undefined) {
        /* elemen belum ke-render (render pertama): pakai default,
           select = opsi pertama, teks = kosong. Tanpa ini showIf tidak
           pernah match di render awal = form blank (bug) */
        vals[inp.id] = inp.type === "select" ? inp.opts[0][0] : "";
      }
    });
    return vals;
  }

  function escHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) => (
      { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function matrixPreview(text) {
    /* LaTeX pmatrix (dari mathfield) → teruskan apa adanya;
       "1,2;3,4" legacy → LaTeX pmatrix. Dirender KaTeX. */
    text = String(text || "").trim();
    if (/\\begin\{[pbvB]matrix\}/.test(text)) return text;
    const rows = text.split(";").map((r) =>
      r.trim()).filter(Boolean).map((r) =>
        (r.match(/[^,\s]+/g) || []).join(" & "));
    if (!rows.length) return "";
    return "\\begin{pmatrix}" + rows.join(" \\\\ ") + "\\end{pmatrix}";
  }

  function renderForm() {
    if (!current) return;
    const wrap = $("toolForm");
    /* simpan isi mf (LaTeX mentah) sebelum HTML ditimpa, jaga agar
       ganti mode tidak menghapus apa yang udah diketik user */
    const savedMf = {};
    wrap.querySelectorAll("math-field").forEach((mf) => {
      if (mf.id && mf.id.startsWith("ti_")) {
        const raw = (mf.getValue ? mf.getValue() : mf.value) || "";
        if (raw.trim()) savedMf[mf.id.slice(3)] = raw;
      }
    });
    const vals = collect();
    /* mode EFEKTIF: di mode Auto, field mengikuti operator yang
       TERDETEKSI di mathfield (bukan sekadar mode terpilih) */
    const effVals = (currentId === "integral" && vals.mode === "auto")
      ? Object.assign({}, vals,
          { mode: opModeOf(integralDetectedOp()) || "auto" })
      : vals;
    current.__effMode = effVals.mode;   // utk deteksi perubahan live
    let html = "";
    current.inputs.forEach((inp) => {
      if (!visible(inp, effVals)) return;
      const label = inp.plain ? escHtml(inp.label)
        : escHtml(t(inp.label, inp.fb || inp.label));
      let field;
      if (inp.type === "select") {
        const opts = inp.opts.map(([v, lk, fb]) => {
          const sel = vals[inp.id] === v ? " selected" : "";
          return `<option value="${v}"${sel}>${escHtml(t(lk, fb || lk))}</option>`;
        }).join("");
        field = `<select id="ti_${inp.id}">${opts}</select>`;
      } else if (inp.type === "mbuild") {
        /* matrix builder: grid sel klik-ketik ala mathway, +/− baris & kolom */
        field = `<div class="mx-build" data-id="${inp.id}" ` +
          `data-min="${(inp.build && inp.build.min) || 1}" ` +
          `data-max="${(inp.build && inp.build.max) || 6}"></div>` +
          `<input type="hidden" id="ti_${inp.id}" value="${escHtml(vals[inp.id] || inp.def || "")}">`;
      } else if (inp.type === "range") {
        /* slider live: engine grapher update tanpa re-render */
        field = `<div class="rng-wrap"><input type="range" id="ti_${inp.id}" ` +
          `min="${inp.min}" max="${inp.max}" step="${inp.step || 1}" ` +
          `value="${escHtml(vals[inp.id] || inp.def || inp.min || 0)}">` +
          `<span class="rng-val" id="tiv_${inp.id}">${escHtml(vals[inp.id] || inp.def || "")}</span></div>`;
      } else if (inp.type === "mf") {
        const isi = savedMf[inp.id] !== undefined ? savedMf[inp.id] : (inp.pre || "");
        field = `<math-field id="ti_${inp.id}" placeholder="${escHtml(inp.ph || "")}">${escHtml(isi)}</math-field>`;
      } else if (inp.type === "textarea") {
        field = `<textarea id="ti_${inp.id}" rows="2" placeholder="${escHtml(inp.ph || "")}">${escHtml(vals[inp.id] || "")}</textarea>`;
      } else {
        field = `<input id="ti_${inp.id}" value="${escHtml(vals[inp.id] || inp.def || "")}" placeholder="${escHtml(inp.ph || "")}">`;
      }
      html += `<label><span class="lbl">${label}</span>${field}</label>`;
    });
    /* preview latex utk matriks */
    if (current.matrixIn) {
      html += `<div class="t-preview"><span class="t-preview-lbl">${escHtml(t("tools.matrix.preview", "Tampilan matriks"))}</span><div class="t-preview-body" id="ti_matrixPrev"></div></div>`;
    }
    if (current.hint) {
      html += `<p class="hint">${escHtml(t(current.hint, current.hint))}</p>`;
    }
    /* kotak contoh penggunaan → panel hasil (kanan), tombol 📋 salin */
    wrap.innerHTML = html;
    wrap.classList.toggle("grid2", !!current.wide);
    /* select berubah -> re-render (showIf) */
    wrap.querySelectorAll("select").forEach((s) => {
      s.addEventListener("change", renderForm);
    });
    /* slider live: bubble + engine grapher update instan */
    wrap.querySelectorAll('input[type="range"]').forEach((r) => {
      r.addEventListener("input", () => {
        const bubble = $("tiv_" + r.id.slice(3));
        if (bubble) bubble.textContent = r.value;
        if (currentEngine && window.GRAPH_ENGINES && GRAPH_ENGINES[currentEngine]) {
          const p = collect();
          try { GRAPH_ENGINES[currentEngine].update(p); } catch (e) {}
        }
      });
    });
    /* matrix builder (mbuild): pasang grid + klik-ketik */
    wrap.querySelectorAll(".mx-build").forEach((w) => {
      const hid = $("ti_" + w.dataset.id);
      if (hid) initMxBuild(w, hid, +w.dataset.min, +w.dataset.max);
    });
    /* preview matriks live (mf = LaTeX pmatrix langsung) */
    const mtx = $("ti_matrix");
    const prev = $("ti_matrixPrev");
    if (mtx && prev) {
      const gv = () => (mtx.getValue ? mtx.getValue() : mtx.value) || "";
      const upd = () => { prev.innerHTML = renderLatex(matrixPreview(gv()), true); };
      mtx.addEventListener("input", upd);
      upd();
    }
    /* parameter opsional terkunci "Custom" saat operator di mathfield
       sudah membawa nilai sendiri (batas \int/\sum, titik \lim, orde
       \frac{d^2}{dx^2}) — live update tiap field diedit. Mode Auto:
       operator baru terdeteksi → render ulang SEKALI biar field
       parameter yang relevan muncul (fokus dikembalikan ke field). */
    const exf = $("ti_expr");
    if (exf) {
      exf.addEventListener("input", () => {
        const sel = $("ti_mode");
        const md = sel ? sel.value : "auto";
        if (md === "auto") {
          const want = opModeOf(integralDetectedOp());
          const last = current.__effMode || "auto";
          if (want && want !== last) {
            renderForm();
            const nm = $("ti_expr");
            if (nm) { try { nm.focus(); } catch (e) {} }
            return;
          }
        }
        updateParamLocks();
      });
      updateParamLocks();
    }
    /* MathLive baru → daftarkan supaya keypad Desmos ikut fokus tool ini */
    if (typeof setupActiveFields === "function") setupActiveFields();
    renderUseBox();
  }

  /* ---------- kunci + AUTO-FILL parameter opsional (tool integral) ----------
     Operator di mathfield yang membawa nilai sendiri (batas bawah/atas
     \int & \sum/\prod, titik \lim, orde eksplisit \frac{d^2}{dx^2})
     membuat field parameter yang tumpang-tindih: DISABLED + tag "Custom"
     + NILAI DI-ISI OTOMATIS dr editor (gak ada tabrakan, gak ada field
     kosong yang bikin parse error). Hapus nilai di editor → field aktif
     lagi. Mode Auto: field tampil/hilang mengikuti operator terdeteksi. */
  function updateParamLocks() {
    if (currentId !== "integral") return;
    const mf = $("ti_expr");
    if (!mf) return;
    const modeSel = $("ti_mode");
    const md = modeSel ? modeSel.value : "auto";
    const opd = integralDetectedOp();
    const custom = {};   // field id -> nilai dr editor (auto-fill)
    if (opd) {
      if (opd.op === "integral" && opd.has_bounds) {
        custom.a = opd.a; custom.b = opd.b;
      }
      if (opd.op === "sum" || opd.op === "product") {
        custom.a = opd.a; custom.b = opd.b;
      }
      if (opd.op === "limit" && opd.at !== undefined) custom.x0 = opd.at;
      /* orde EKSPLISIT di editor (d^2/dx^2 / multi-var) → field n terkunci
         + terisi; \frac{d}{dx} polos tetap bisa diisi (field n = override) */
      if (opd.op === "derivative" && ((opd.order || 1) > 1 || opd.vars))
        custom.n = String(opd.order || (opd.vars ? "" : 1));
      /* turunan + bar evaluasi (\bigm{|}_{x=2} dsb): orde & titik keduanya
         ada di editor → n DAN xo terkunci Custom + terisi */
      if (opd.op === "subs_deriv") {
        const inner = opd.sub || {};
        if (inner.op === "derivative")
          custom.n = String(inner.order || 1);
        if (opd.point !== undefined && opd.point !== "")
          custom.xo = String(opd.point);
      }
    }
    ["a", "b", "x0", "n", "xo"].forEach((k) => {
      const el = $("ti_" + k);
      if (!el) return;
      const lbl = el.closest("label");
      const val = custom[k];
      const isCustom = val !== undefined && val !== "";
      if (isCustom) {
        el.disabled = true;
        el.classList.add("param-custom");
        if (String(el.value) !== String(val)) el.value = val;   // AUTO-FILL
        if (lbl && !lbl.querySelector(".custom-tag")) {
          const tag = document.createElement("span");
          tag.className = "custom-tag";
          tag.textContent = "Custom";
          const lblSpan = lbl.querySelector(".lbl") || lbl;
          lblSpan.appendChild(tag);
        }
      } else {
        el.disabled = false;
        el.classList.remove("param-custom");
        if (lbl) {
          const tg = lbl.querySelector(".custom-tag");
          if (tg) tg.remove();
        }
      }
      /* mode Auto: tampilkan field hanya jika relevan dgn operator
         terdeteksi (tanpa ini field operasi lain nyangkut di form) */
      if (lbl) {
        if (md === "auto") {
          const relevan =
            (opd && opd.op === "subs_deriv" && (k === "n" || k === "xo")) ||
            (opd && opd.op === "integral" && (k === "a" || k === "b") && opd.has_bounds) ||
            (opd && (opd.op === "sum" || opd.op === "product") && (k === "a" || k === "b")) ||
            (opd && opd.op === "limit" && k === "x0") ||
            (opd && opd.op === "derivative" && (k === "n" ? isCustom : k === "xo"));
          lbl.style.display = relevan ? "" : "none";
        } else {
          lbl.style.display = "";
        }
      }
    });
  }

  /* Contoh penggunaan: panel kanan, di bawah hasil; tombol 📋 = copy
     LaTeX mentah baris itu ke clipboard (guna: paste ke field mana pun).
     Tiap baris di-resolve dr i18n dulu (grup tools.<id>.use<n> / sims.<id>.use<n>)
     biar fragmen \text{} ikut bahasa aktif; tanpa kunci = LaTeX fallback registry. */
  function renderUseBox() {
    const ub = $("toolUseBox");
    if (!ub) return;
    if (current.use && current.use.length) {
      const grp = SIM_IDS.has(currentId) ? "sims" : "tools";
      const resolved = current.use.map((u, i) =>
        t(grp + "." + currentId + ".use" + (i + 1), u));
      current.__useRes = resolved;
      ub.className = "use-box";
      ub.innerHTML = `<div class="use-h">${escHtml(t("tools.use", "Contoh penggunaan"))}</div>` +
        resolved.map((u, i) =>
          `<div class="use-row"><div class="use-math">${renderLatex(u, true)}</div>` +
          `<button class="use-copy" type="button" data-i="${i}" title="Salin LaTeX ke clipboard" aria-label="Salin LaTeX">📋</button></div>`).join("");
      ub.querySelectorAll(".use-copy").forEach((btn) => {
        btn.onclick = async () => {
          const la = (current.__useRes && current.__useRes[+btn.dataset.i]) || "";
          const labelAsal = btn.textContent;
          try {
            await navigator.clipboard.writeText(la);
            btn.textContent = "✅";
          } catch (e) {
            /* fallback clipboard lama */
            try {
              const ta = document.createElement("textarea");
              ta.value = la;
              document.body.appendChild(ta);
              ta.select();
              document.execCommand("copy");
              ta.remove();
              btn.textContent = "✅";
            } catch (e2) {
              btn.textContent = "✖";
            }
          }
          setTimeout(() => { btn.textContent = labelAsal; }, 1100);
        };
      });
    } else {
      ub.className = "hidden";
      ub.innerHTML = "";
    }
  }

  /* ---------- render hasil ---------- */
  function renderResult(data) {
    const box = $("toolResult");
    const parts = [];
    if (data.matrix_in && typeof renderLatex === "function") {
      parts.push(`<div class="math-res-box">${renderLatex(data.matrix_in)}</div>`);
    }
    if (data.rows) {
      parts.push('<div class="lab-rows">' + data.rows.map(([k, v, isL]) => {
        let label = "";
        if (current.labels && current.labels[k] !== undefined && current.labels[k] !== "") {
          label = escHtml(t(current.labels[k], current.labels[k]));
        }
        let val = v;
        if (current.labels2 && current.labels2[k] !== undefined) {
          label = escHtml(t(current.labels2[k], current.labels2[k]));
        }
        if (!isL && typeof v === "string" && VALUE_MAP[v]) val = t(VALUE_MAP[v], v);
        if (isL && typeof v === "string" && NOTE_KEYS[v]) val = t(NOTE_KEYS[v], v);
        const body = isL && typeof renderLatex === "function"
          ? renderLatex(val, true) : escHtml(val);
        return `<div class="lab-row">${label ? `<div class="lab-k">${label}</div>` : ""}<div class="lab-v">${body}</div></div>`;
      }).join("") + "</div>");
    } else if (data && typeof data === "object" && !data.plot) {
      /* hasil flat dict (mis. stats): tiap kunci = satu baris */
      parts.push('<div class="lab-rows">' + Object.entries(data).filter(([k]) =>
        k !== "matrix_in" && k !== "plot").map(([k, v]) => {
          let label = "";
          if (current.labels2 && current.labels2[k] !== undefined) {
            label = escHtml(t(current.labels2[k], current.labels2[k]));
          }
          return `<div class="lab-row">${label ? `<div class="lab-k">${label}</div>` : ""}<div class="lab-v">${escHtml(v)}</div></div>`;
        }).join("") + "</div>");
    }
    box.className = "";
    box.innerHTML = parts.join("") || "&mdash;";

    // plot (mis. gerak parabola), dukung single-trace lama & multi-trace sim
    const plotEl = $("toolPlot");
    const P = data.plot;
    if (P && window.Plotly && (P.traces || P.x)) {
      plotEl.classList.remove("hidden");
      const preset = (typeof getActivePreset === "function") ? getActivePreset() : null;
      const base = (preset && preset.curve) || "#e0b04a";
      const PAL = ["#7fb4d8", "#d87f7f", "#9fd89f", "#c79fd8", "#d8c07f", "#8fd8d0"];
      let traces;
      if (P.traces) {
        traces = P.traces.map((tr, i) => {
          const isMarker = (tr.mode || "").indexOf("markers") >= 0;
          const out = {
            x: tr.x, y: tr.y,
            mode: tr.mode || "lines",
            line: { color: tr.color || (i ? PAL[(i - 1) % PAL.length] : base),
                    width: tr.mode === "markers" ? 0 : (tr.width || 3),
                    dash: tr.dash || "solid" },
            hoverinfo: "x+y",
          };
          if (isMarker) out.marker = { color: tr.color || base, size: tr.msize || 6 };
          if (tr.fill) out.fill = tr.fill;
          if (tr.opacity != null) out.opacity = tr.opacity;
          return out;
        });
      } else {
        traces = [{
          x: P.x, y: P.y, mode: "lines",
          line: { color: base, width: 4 },
          hoverinfo: "x+y",
        }];
      }
      /* layout 2D bertema (layout2d dr app.js): grid/warna ikut tema web +
         dragmode PAN; judul sumbu dr simlab menimpa default dgn font sama */
      const lay = (typeof layout2d === "function") ? layout2d() : {};
      if (P.xlabel) lay.xaxis = Object.assign({}, lay.xaxis,
        { title: { text: P.xlabel, font: { size: 13, color: lay.font.color } } });
      if (P.ylabel) lay.yaxis = Object.assign({}, lay.yaxis,
        { title: { text: P.ylabel, font: { size: 13, color: lay.font.color } } });
      Plotly.newPlot("toolPlot", traces, lay,
        { responsive: true, displaylogo: false, scrollZoom: true });
    } else {
      plotEl.classList.add("hidden");
    }

    /* advanced graphers: engine interaktif ke #toolCanvas / #toolPlot */
    currentEngine = "";
    lastEngineParams = null;
    const cv = $("toolCanvas");
    if (cv) cv.classList.add("hidden");
    if (data.engine && window.GRAPH_ENGINES && GRAPH_ENGINES[data.engine]) {
      currentEngine = data.engine;
      lastEngineParams = data.params;
      if (window.__GRAPH_CLEAR) window.__GRAPH_CLEAR();   // dispose loop lama
      const eng = GRAPH_ENGINES[data.engine];
      if (eng.kind === "canvas" && cv) {
        plotEl.classList.add("hidden");
        cv.classList.remove("hidden");
        try { eng.mount(cv, data.params); } catch (e) {
          cv.getContext("2d").fillText(errText({ error: "Engine error: " + e.message }), 10, 20);
        }
      } else if (eng.kind === "plotly") {
        cv.classList.add("hidden");
        plotEl.classList.remove("hidden");
        try { eng.mount(_plotlyInner(), data.params); } catch (e) {
          _plotlyInner().textContent = errText({ error: "Engine error: " + e.message });
        }
      }
    }
  }

  /* ---------- open/close ---------- */
  function openTool(id, card) {
    const tool = TOOLS[id];
    if (!tool) return;
    stopGraphEngine();                   // WAJIB: loop grapher lama mati dulu
    current = tool;
    currentId = id;
    lastData = null;
    /* BUGFIX: bersihkan form tool SEBELUMNYA dulu. Kalau tidak, collect()
       masih menemukan elemen ti_* milik tool lama (id kembar beda isi,
       mis. ti_mode isinya mode tool lain) -> showIf tidak match -> form
       tampil blank sampai user ganti dropdown bolak-balik. */
    $("toolForm").innerHTML = "";
    document.querySelectorAll(".panel-wrap").forEach((p) =>
      p.classList.toggle("active", p.id === "tool"));
    document.body.classList.remove("warfs", "hud-show");
    // tandai menu war tersembunyi supaya rantai ESC balik ke lapis alat
    const mm = $("mathMenu"), pm = $("physMenu");
    if (mm) mm.classList.add("hidden");
    if (pm) pm.classList.add("hidden");
    const title = card && card.querySelector(".wt-title")
      ? card.querySelector(".wt-title").textContent : id;
    $("toolTitle").textContent = title;
    /* suffix "· Bidang Studi" dihapus (ref layout baru), cattag = judul saja */
    $("toolCatTag").textContent = title;
    renderForm();
    const res = $("toolResult");
    res.className = "muted";
    res.textContent = t("calc.result_empty", "Belum ada perhitungan.");
    $("toolMsg").textContent = "";
    $("toolPlot").classList.add("hidden");
    const tcv = $("toolCanvas");
    if (tcv) tcv.classList.add("hidden");
  }
  window.openTool = openTool;
  window.__la2plain = la2plain; /* hook debug */

  $("toolRun").onclick = async () => {
    if (!current) return;
    const msg = $("toolMsg");
    msg.className = "hint";
    msg.textContent = t("graph.calculating", "Menghitung\u2026");
    const payload = {};
    current.inputs.forEach((inp) => { payload[inp.id] = collect()[inp.id]; });
    /* tool integral: operator di input dikirim TERSTRUKTUR (op_data) —
       expr berupa marker __NABLA_OP__<json> di-unwrap di sini */
    if (currentId === "integral" &&
        typeof payload.expr === "string" &&
        payload.expr.startsWith("__NABLA_OP__")) {
      try {
        payload.op_data = JSON.parse(payload.expr.slice(12));
        payload.expr = "";
      } catch (e) { /* biarkan backend yang kasih error */ }
      /* mode manual yang GAK sesuai operator di input → AUTO-SWITCH ke
         operasi terdeteksi (mis. Σ di mode Derivative -> mode Σ), form
         ikut re-render biar field-nya yang relevan. Backend sendiri sudah
         menghitung operator di input apa pun mode-nya — ini konsistensi UI */
      const want = opModeOf(payload.op_data);
      const sel = $("ti_mode");
      if (want && sel && sel.value !== want) {
        sel.value = want;
        sel.dispatchEvent(new Event("change"));   // renderForm ulang
        current.inputs.forEach((inp) => { payload[inp.id] = collect()[inp.id]; });
        if (typeof payload.expr === "string" &&
            payload.expr.startsWith("__NABLA_OP__")) {
          try {
            payload.op_data = JSON.parse(payload.expr.slice(12));
            payload.expr = "";
          } catch (e) {}
        }
      }
    }
    try {
      const r = await fetch("/api/lab", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool: currentId, data: payload }),
      });
      const j = await r.json();
      if (!j.ok) {
        msg.className = "hint err";
        msg.textContent = errText(j);
        lastErrJ = j;
        return;
      }
      lastData = j.data;
      lastErrJ = null;
      renderResult(j.data);
      msg.textContent = "";
    } catch (e) {
      msg.className = "hint err";
      msg.textContent = e.message;
    }
  };

  $("toolBack").onclick = () => {
    stopGraphEngine();                     // WAJIB: matikan loop grapher
    const tab = document.querySelector(".tab.active");
    if (tab && tab.dataset.tab === "math" && window.warNav) window.warNav.toMathTools();
    else if (tab && tab.dataset.tab === "physics" && window.warNav) window.warNav.toPhysTools();
    else if (window.warFieldSel) window.warFieldSel.show();
  };

  // tombol Enter di keypad (kpSubmit) rute ke sini via app.js (#toolRun)

  /* MATIKAN engine grapher aktif: dispose RAF/interval/listener + sembunyikan
     canvas. Dipanggil SETIAP perpindahan panel (openTool/toolBack/warp/tab)
     — kalau tidak, loop Ising/fluid/domain terus jalan di background = lag. */
  /* plotly mengukur clientHeight kontainer (padding IKUT terhitung) ->
     svg-nya bisa lebih tinggi dr area konten & nimpa bar note di bawah.
     Solusi: engine di-mount ke div dalam tanpa padding biar ukurannya pas. */
  function _plotlyInner() {
    const pl = $("toolPlot");
    let inner = pl.querySelector(".plot-inner");
    if (!inner) {
      inner = document.createElement("div");
      inner.className = "plot-inner";
      pl.appendChild(inner);
    }
    return inner;
  }

  function stopGraphEngine() {
    /* engine plotly dengan timer sendiri (mis. gpvcycle dot): destroy dulu */
    if (currentEngine && window.GRAPH_ENGINES && GRAPH_ENGINES[currentEngine] &&
        typeof GRAPH_ENGINES[currentEngine].destroy === "function") {
      try { GRAPH_ENGINES[currentEngine].destroy(); } catch (e) {}
    }
    currentEngine = "";
    lastEngineParams = null;
    if (window.__GRAPH_CLEAR) window.__GRAPH_CLEAR();
    const cv = $("toolCanvas");
    if (cv) cv.classList.add("hidden");
    /* plot container sisa engine plotly juga dirapikan (purge div dalam) */
    const pl = $("toolPlot");
    const inner = pl && pl.querySelector(".plot-inner");
    if (inner && window.Plotly && Plotly.purge) Plotly.purge(inner);
    if (pl) Plotly && window.Plotly && Plotly.purge && Plotly.purge(pl);
  }
  window.__GRAPH_STOP = stopGraphEngine;   // dipakai menu.js saat pindah panel

  /* ganti tema -> tool plot aktif re-render dgn warna tema baru (hook app.js) */
  window.toolThemeRefresh = () => {
    if (!current || !lastData) return;
    const sec = $("tool");
    if (sec && sec.classList.contains("active")) {
      if (lastData.plot) renderResult(lastData);
      /* engine grapher: re-mount dengan params sama (warna tema baru) */
      if (currentEngine && window.GRAPH_ENGINES && GRAPH_ENGINES[currentEngine]
          && lastEngineParams) {
        const eng = GRAPH_ENGINES[currentEngine];
        const cv = $("toolCanvas");
        if (eng.kind === "canvas" && cv && !cv.classList.contains("hidden")) {
          try { eng.mount(cv, lastEngineParams); } catch (e) {}
        } else if (eng.kind === "plotly") {
          try { eng.mount(_plotlyInner(), lastEngineParams); } catch (e) {}
        }
      }
    }
  };

  /* ---------- ganti bahasa SAAT panel tool terbuka ----------
     Handler ini jalan SETELAH translateAll (urutan di setLang), jadi
     judul kartu .wt-title sudah diterjemahkan, tinggal dibaca ulang.
     Semua elemen panel di-render ulang: form (label+opsi), use-box,
     hasil (label row), dan judul. Isian user dipertahankan renderForm. */
  if (window.I18N && I18N.onChange) {
    I18N.onChange(() => {
      if (!current || !currentId) return;
      const sec = $("tool");
      if (!sec || !sec.classList.contains("active")) return;
      const card = document.querySelector(
        '#mathMenu .wtile[data-tool=' + currentId + '], ' +
        '#physMenu .wtile[data-tool=' + currentId + ']');
      const tEl = card ? card.querySelector(".wt-title") : null;
      if (tEl) {
        $("toolTitle").textContent = tEl.textContent;
        $("toolCatTag").textContent = tEl.textContent;
      }
      renderForm();
      if (lastErrJ) {
        $("toolMsg").className = "hint err";
        $("toolMsg").textContent = errText(lastErrJ);   // error ikut bahasa baru
      }
      if (lastData) renderResult(lastData);
      else if (!lastErrJ) {
        const res = $("toolResult");
        res.className = "muted";
        res.textContent = t("calc.result_empty", "Belum ada perhitungan.");
        $("toolMsg").textContent = "";
      }
    });
  }
})();
