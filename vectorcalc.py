"""Vector / multivariable calculus built on SymEngine.

SymEngine only provides the basics (diff, Matrix, Lambdify, ...), so the
vector-calculus operators (gradient, divergence, curl, Laplacian, Hessian,
Jacobian, directional derivative) are implemented here on top of `diff`.
"""
import numpy as np
import symengine as se

X, Y, Z, T = se.symbols("x y z t")
VARS = (X, Y, Z)
MAX_LEN = 300


class CalcError(ValueError):
    """User-facing error (bad input, unsupported operation, ...).
    key + args opsional untuk i18n frontend (fallback = msg Indonesia)."""

    def __init__(self, msg, key=None, *args):
        super().__init__(msg)
        self.key = key
        self.i18n_args = list(args)


import re

# ----------------------------------------------------------------- parsing
def _parse_braced(s, start_idx):
    if start_idx >= len(s) or s[start_idx] != "{":
        return None, start_idx
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start_idx + 1 : i], i + 1
    return None, len(s)


def _parse_bracket(s, start_idx):
    if start_idx >= len(s) or s[start_idx] != "[":
        return None, start_idx
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == "[":
            depth += 1
        elif s[i] == "]":
            depth -= 1
            if depth == 0:
                return s[start_idx + 1 : i], i + 1
    return None, len(s)


STYLE_CMDS = (
    r"\bm", r"\boldsymbol", r"\mathbf", r"\textbf", r"\mathit", r"\textit",
    r"\mathrm", r"\textrm", r"\text", r"\mathsf", r"\mathtt", r"\mathbb",
    r"\mathcal", r"\mathscr", r"\mathfrak", r"\operatorname", r"\boldmath",
)


def strip_latex_styles(s):
    """Strip all font styling wrappers like \\bm{...}, \\mathbf{...}, \\mathrm{...}, etc."""
    if not s:
        return ""
    # remove parameterless style declarations
    s = re.sub(
        r"\\(?:boldmath|displaystyle|textstyle|scriptstyle|scriptscriptstyle|bf|it|rm|sf|tt)\b",
        "",
        s,
    )
    # remove \textcolor{color}{content} or \color{color}{content}
    while True:
        m = re.search(r"\\(?:color|textcolor)\s*\{", s)
        if not m:
            break
        _, k1 = _parse_braced(s, m.end() - 1)
        while k1 < len(s) and s[k1].isspace():
            k1 += 1
        if k1 < len(s) and s[k1] == "{":
            content, k2 = _parse_braced(s, k1)
            s = s[: m.start()] + content + s[k2:]
        else:
            s = s[: m.start()] + s[k1:]

    # unwrap commands with single braced or single token argument
    changed = True
    while changed:
        changed = False
        for cmd in STYLE_CMDS:
            idx = 0
            while True:
                found = s.find(cmd, idx)
                if found == -1:
                    break
                k = found + len(cmd)
                while k < len(s) and s[k].isspace():
                    k += 1
                if k < len(s) and s[k] == "{":
                    inner, end_k = _parse_braced(s, k)
                    if inner is not None:
                        s = s[:found] + inner + s[end_k:]
                        changed = True
                        idx = found + len(inner)
                        continue
                elif k < len(s) and (s[k].isalnum() or s[k] == "\\"):
                    if s[k] == "\\":
                        m_cmd = re.match(r"\\[a-zA-Z]+", s[k:])
                        if m_cmd:
                            char_len = len(m_cmd.group(0))
                            inner = s[k : k + char_len]
                            s = s[:found] + inner + s[k + char_len :]
                            changed = True
                            idx = found + len(inner)
                            continue
                    else:
                        inner = s[k]
                        s = s[:found] + inner + s[k + 1 :]
                        changed = True
                        idx = found + 1
                        continue
                idx = found + len(cmd)
    return s


def _prep_sympy(raw):
    """Prep a raw expression string for sympy: implicit multiplication + ^ -> **."""
    s = raw.strip()
    # convert ^ to ** first (careful with already ** sequences)
    s = s.replace("^", "**")
    # implicit mult: digit followed by letter/(
    s = re.sub(r"(\d+)\s*([a-zA-Z(])", r"\1*\2", s)
    # ) followed by letter/digit/(
    s = re.sub(r"(\))\s*([a-zA-Z0-9(])", r"\1*\2", s)
    # replace \pi with pi
    s = s.replace(r"\pi", "pi")
    return s


def eval_calculus_latex(s):
    """Evaluate calculus operators like definite integrals and derivatives before general parsing."""
    import sympy as sp

    # 1. Strip all font styles (bm, mathbf, mathrm, etc.)
    s = strip_latex_styles(s)

    # 2. Clean spacing commands & brackets
    s = re.sub(r"\\[,;:! ]", " ", s)
    s = s.replace("~", " ")
    s = s.replace(r"\left(", "(").replace(r"\right)", ")")
    s = s.replace(r"\left[", "[").replace(r"\right]", "]")

    # Ensure LaTeX space commands are converted to spaces
    s = s.replace("\\,", " ").replace("\\:", " ").replace("\\;", " ")

    # 3. Clean accidental commas or thin spaces before differential symbol
    s = re.sub(r",\s*d([xyzt])\b", r" d\1", s)

    # 4. Definite integrals: \int_{lower}^{upper} body d(var) or \int_a^b body d(var)
    int_def_pattern = r"\\int_(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))\^(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))\s*(.*?)\s*d([xyzt])\b"

    def repl_def_int(m):
        lo_raw = _prep_sympy(latex_to_raw(m.group(1) or m.group(2)))
        hi_raw = _prep_sympy(latex_to_raw(m.group(3) or m.group(4)))
        body_raw = _prep_sympy(latex_to_raw(m.group(5)))
        var_str = m.group(6).strip()
        try:
            var = sp.Symbol(var_str)
            lo = sp.sympify(lo_raw)
            hi = sp.sympify(hi_raw)
            body = sp.sympify(body_raw)
            res = sp.integrate(body, (var, lo, hi))
            return f"({res})"
        except Exception:
            return "(0)"

    s = re.sub(int_def_pattern, repl_def_int, s)

    # 5. Indefinite integrals: \int body d(var) (if not followed by _)
    if not re.search(r"\\int_", s):
        int_indef_pattern = r"\\int\s*(.*?)\s*d([xyzt])\b"

        def repl_indef_int(m):
            body_raw = _prep_sympy(latex_to_raw(m.group(1)))
            var_str = m.group(2).strip()
            try:
                var = sp.Symbol(var_str)
                body = sp.sympify(body_raw)
                res = sp.integrate(body, var)
                return f"({res})"
            except Exception:
                return "(0)"

        s = re.sub(int_indef_pattern, repl_indef_int, s)

    # 6. Derivatives: \frac{\partial^n}{\partial x^n}(expr) or \frac{d^n}{dx^n}(expr)
    diff_pattern = r"\\frac\{(?:\\partial|d)(?:\^(\d+))?\}\{(?:\\partial|d)\s*([xyzt])(?:\^\1)?\}\s*(?:\(([^()]+)\)|([0-9a-zA-Z]+))"

    def repl_diff(m):
        order = int(m.group(1) or 1)
        var_str = m.group(2).strip()
        expr_raw = _prep_sympy(latex_to_raw(m.group(3) or m.group(4)))
        try:
            var = sp.Symbol(var_str)
            expr = sp.sympify(expr_raw)
            res = sp.diff(expr, var, order)
            return f"({res})"
        except Exception:
            return "(0)"

    s = re.sub(diff_pattern, repl_diff, s)

    # 7. Sums: \sum_{lower}^{upper} body
    sum_pattern = r"\\sum_(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))\^(?:\{([^}]+)\}|(\\[a-zA-Z]+|[0-9a-zA-Z]))"
    # Find all sum limits and replace each sum expression with its evaluated value
    parts = []
    last_end = 0
    for match in re.finditer(sum_pattern, s):
        # Text before the match
        parts.append(s[last_end:match.start()])
        # Extract limits
        lo_raw = latex_to_raw(match.group(1) or match.group(2))
        hi_raw = latex_to_raw(match.group(3) or match.group(4))
        # Find body start: after the match, skip whitespace
        body_start = match.end()
        while body_start < len(s) and s[body_start].isspace():
            body_start += 1
        # Parse body until we encounter a space or operator (+, -, *, /, ^, =) at brace depth zero
        depth = 0
        body_end = body_start
        while body_end < len(s):
            ch = s[body_end]
            if ch == '{':
                depth += 1
            elif ch == '}':
                if depth == 0:
                    # Unmatched closing brace, treat as end
                    break
                depth -= 1
            elif depth == 0 and ch in '+-*/^=':
                # Stop at operator at brace level zero
                break
            body_end += 1
        body_raw = s[body_start:body_end]
        try:
            # Parse lower limit: if it contains an '=', split into index and start
            if '=' in lo_raw:
                index_str, start_str = lo_raw.split('=', 1)
            else:
                # Fallback: assume index is 'n' and the whole lower limit is the start
                index_str = 'n'
                start_str = lo_raw
            end_str = hi_raw
            index = sp.Symbol(index_str.strip())
            start = sp.sympify(_prep_sympy(start_str.strip()))
            end = sp.sympify(_prep_sympy(end_str.strip()))
            # Apply implicit multiplication to body before sympify
            body = sp.sympify(_prep_sympy(body_raw))
            res = sp.summation(body, (index, start, end))
            replacement = f"({res})"
        except Exception:
            # If evaluation fails, use 0 so downstream parsing doesn't break
            replacement = "(0)"
        parts.append(replacement)
        last_end = body_end
    # Append remaining part of the string
    parts.append(s[last_end:])
    s = ''.join(parts)

    return s


def latex_to_raw(s):
    """Convert LaTeX math input (from MathLive or manual entry) to raw SymEngine expression."""
    if not s:
        return ""
    # Strip font styling wrappers first
    s = strip_latex_styles(s)
    s = s.strip()

    # 1. Clean formatting commands & wrappers
    s = re.sub(r"\\(?:displaystyle|textstyle|scriptstyle)", "", s)
    s = re.sub(r"\\left\b|\\right\b", "", s)
    s = re.sub(r"\\[,;:! ]", " ", s)
    s = s.replace("~", " ")
    s = re.sub(r"\\cdot|\\times", "*", s)
    s = re.sub(r"\\div", "/", s)
    s = re.sub(r"\\pi\b", "pi", s)

    # Convert \sin^2(x) -> (sin(x))**2 pattern
    s = re.sub(
        r"\\(sin|cos|tan|sec|csc|cot|sinh|cosh|tanh|ln|log)\^\{?([0-9a-zA-Z]+)\}?\s*(\([^\)]+\)|[xyzt])",
        r"(\1(\3))**(\2)",
        s,
    )

    # 2. Recursively expand \frac and \sqrt
    out = []
    i = 0
    while i < len(s):
        if s.startswith(r"\frac", i):
            k = i + 5
            while k < len(s) and s[k].isspace():
                k += 1
            num, k2 = _parse_braced(s, k)
            if num is not None:
                while k2 < len(s) and s[k2].isspace():
                    k2 += 1
                den, k3 = _parse_braced(s, k2)
                if den is not None:
                    out.append(f"(({latex_to_raw(num)})/({latex_to_raw(den)}))")
                    i = k3
                    continue
        elif s.startswith(r"\sqrt", i):
            k = i + 5
            while k < len(s) and s[k].isspace():
                k += 1
            root_deg, k2 = _parse_bracket(s, k)
            if root_deg is not None:
                while k2 < len(s) and s[k2].isspace():
                    k2 += 1
                arg, k3 = _parse_braced(s, k2)
                if arg is not None:
                    out.append(f"(({latex_to_raw(arg)})**(1/({latex_to_raw(root_deg)})))")
                    i = k3
                    continue
            else:
                arg, k3 = _parse_braced(s, k)
                if arg is not None:
                    out.append(f"sqrt({latex_to_raw(arg)})")
                    i = k3
                    continue
        out.append(s[i])
        i += 1
    s = "".join(out)

    # 3. Standard functions mapping
    fn_map = {
        r"\sin": "sin", r"\cos": "cos", r"\tan": "tan",
        r"\sec": "sec", r"\csc": "csc", r"\cot": "cot",
        r"\arcsin": "asin", r"\arccos": "acos", r"\arctan": "atan",
        r"\asin": "asin", r"\acos": "acos", r"\atan": "atan",
        r"\sinh": "sinh", r"\cosh": "cosh", r"\tanh": "tanh",
        r"\ln": "log", r"\log": "log", r"\exp": "exp",
    }
    for k, v in fn_map.items():
        s = re.sub(re.escape(k) + r"(?![a-zA-Z])", v, s)

    # Replace remaining braces {arg} with (arg)
    s = s.replace("{", "(").replace("}", ")")
    s = s.replace("^", "**")

    # Absolute values |x| -> abs(x)
    s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)

    # 4. Implicit multiplication
    # Number followed by variable or ( or function
    s = re.sub(r"(\d+)\s*([a-zA-Z(])", r"\1*\2", s)
    # ) followed by ( or variable or number
    s = re.sub(r"(\))\s*([a-zA-Z0-9(])", r"\1*\2", s)

    fns = "sin|cos|tan|sec|csc|cot|asin|acos|atan|sinh|cosh|tanh|log|exp|sqrt|abs|pi"
    # var x, y, z, t followed by function
    s = re.sub(r"\b([xyzt])\s*(" + fns + r")\b", r"\1*\2", s)
    # var followed by var (consecutive)
    while re.search(r"\b([xyzt])\s+([xyzt])\b", s):
        s = re.sub(r"\b([xyzt])\s+([xyzt])\b", r"\1*\2", s)
    # var followed by (
    while re.search(r"\b([xyzt])\s*\(", s):
        s = re.sub(r"\b([xyzt])\s*\(", r"\1*(", s)

    return s


def parse(text, allowed=VARS):
    raw_text = (text or "").strip()
    if not raw_text:
        raise CalcError("Ekspresi kosong.", "err.expr_empty")
    if len(raw_text) > MAX_LEN:
        raise CalcError("Ekspresi terlalu panjang.", "err.expr_long")

    cleaned = strip_latex_styles(raw_text)
    cleaned = eval_calculus_latex(cleaned)
    cleaned = latex_to_raw(cleaned)
    try:
        expr = se.sympify(cleaned)
    except Exception as exc:  # noqa: BLE001
        raise CalcError(f"Tidak bisa membaca ekspresi '{raw_text}': {exc}",
                       "err.expr_parse", str(exc))
    extra = {str(s) for s in expr.free_symbols} - {str(a) for a in allowed}
    if extra:
        raise CalcError(
            f"Variabel tidak dikenal: {', '.join(sorted(extra))}. "
            f"Gunakan: {', '.join(str(a) for a in allowed)}.",
            "err.unknown_var", ", ".join(sorted(extra))
        )
    return expr


def fmt(expr):
    """Expression -> readable string."""
    return str(expr).replace("**", "^")


def fmt_vec(vec):
    return [fmt(c) for c in vec]


def to_latex(expr):
    try:
        return se.latex(expr)
    except Exception:
        return fmt(expr)


def to_latex_vec(vec):
    return [to_latex(c) for c in vec]


# ------------------------------------------------------- vector calculus ops
def partial(f, var, order=1):
    for _ in range(order):
        f = se.diff(f, var)
    return se.expand(f)


def gradient(f, vars_=VARS):
    return [se.expand(se.diff(f, v)) for v in vars_]


def divergence(F, vars_=VARS):
    return se.expand(sum(se.diff(c, v) for c, v in zip(F, vars_)))


def curl(F, vars_=VARS):
    P, Q, R = F
    x, y, z = vars_
    return [
        se.expand(se.diff(R, y) - se.diff(Q, z)),
        se.expand(se.diff(P, z) - se.diff(R, x)),
        se.expand(se.diff(Q, x) - se.diff(P, y)),
    ]


def laplacian(f, vars_=VARS):
    return se.expand(sum(se.diff(f, v, 2) for v in vars_))


def hessian(f, vars_=VARS):
    return [[se.expand(se.diff(se.diff(f, a), b)) for b in vars_] for a in vars_]


def jacobian(F, vars_=VARS):
    return [[se.expand(se.diff(c, v)) for v in vars_] for c in F]


def directional(f, direction, vars_=VARS):
    norm = se.sqrt(sum(d ** 2 for d in direction))
    return sum(g * d for g, d in zip(gradient(f, vars_), direction)) / norm


# ------------------------------------------------------- numeric evaluation
def num(expr, *arrays):
    """Evaluate `expr(x, y, z)` numerically on equal-length 1-D arrays."""
    arrays = [np.asarray(a, dtype=float).ravel() for a in arrays]
    n = arrays[0].size
    args = list(VARS[: len(arrays)]) if len(arrays) <= 3 else list(VARS)
    expr = se.sympify(expr)
    if not expr.free_symbols:
        return np.full(n, float(expr))
    fn = se.Lambdify(args, expr, real=True)
    # SymEngine's Lambdify wants ONE array of shape (n, n_args), not separate arrays
    data = arrays[0] if len(arrays) == 1 else np.stack(arrays, axis=-1)
    with np.errstate(all="ignore"):
        out = np.asarray(fn(np.ascontiguousarray(data)), dtype=float).ravel()
    if out.size == 1 and n > 1:
        out = np.full(n, out[0])
    return out


def num_t(expr, t):
    t = np.asarray(t, dtype=float).ravel()
    expr = se.sympify(expr)
    if not expr.free_symbols:
        return np.full(t.size, float(expr))
    fn = se.Lambdify([T], expr, real=True)
    with np.errstate(all="ignore"):
        out = np.asarray(fn(t), dtype=float).ravel()
    if out.size == 1 and t.size > 1:
        out = np.full(t.size, out[0])
    return out


def at_point(expr, point):
    x, y, z = point
    v = float(num(expr, [x], [y], [z])[0])
    return None if not np.isfinite(v) else v


def clean(arr):
    """numpy -> JSON-safe list (NaN/inf -> None)."""
    return [None if not np.isfinite(v) else float(v) for v in np.asarray(arr, float).ravel()]


# ------------------------------------------------------------ calc dispatcher
SCALAR_OPS = {"partial", "gradient", "laplacian", "hessian", "directional"}
VECTOR_OPS = {"divergence", "curl", "jacobian"}


def calculate(op, f=None, F=None, point=None, order=1, var="x", direction=None):
    out = {"op": op}
    if op in SCALAR_OPS:
        fx = parse(f)
        out["input"] = fmt(fx)
        out["input_latex"] = to_latex(fx)
        if op == "partial":
            v = {"x": X, "y": Y, "z": Z}.get(var)
            if v is None:
                raise CalcError("Variabel harus x, y, atau z.", "err.var_xyz")
            order = max(1, min(int(order or 1), 6))
            r = partial(fx, v, order)
            ord_str = f"^{order}" if order > 1 else ""
            out.update(
                kind="scalar",
                result=fmt(r),
                latex=to_latex(r),
                label=f"∂{ord_str}f/∂{var}{ord_str}",
                label_latex=f"\\frac{{\\partial{ord_str} f}}{{\\partial {var}{ord_str}}}",
            )
            _eval(out, [r], point, "scalar")
        elif op == "gradient":
            r = gradient(fx)
            out.update(
                kind="vector",
                result=fmt_vec(r),
                latex=to_latex_vec(r),
                label="∇f",
                label_latex="\\nabla f",
            )
            _eval(out, r, point, "vector")
        elif op == "laplacian":
            r = laplacian(fx)
            out.update(
                kind="scalar",
                result=fmt(r),
                latex=to_latex(r),
                label="∇²f",
                label_latex="\\nabla^2 f",
            )
            _eval(out, [r], point, "scalar")
        elif op == "hessian":
            H = hessian(fx)
            out.update(
                kind="matrix",
                result=[fmt_vec(row) for row in H],
                latex=[to_latex_vec(row) for row in H],
                label="H(f)",
                label_latex="H(f)",
            )
            if point:
                out["at_point"] = [[at_point(c, point) for c in row] for row in H]
        else:  # directional
            d = [parse(c, allowed=()) for c in (direction or [])]
            if len(d) != 3 or all(float(c) == 0 for c in d):
                raise CalcError("Arah harus 3 angka dan bukan vektor nol.", "err.dir3")
            r = directional(fx, d)
            out.update(
                kind="scalar",
                result=fmt(r),
                latex=to_latex(r),
                label="D_u f",
                label_latex="D_{\\mathbf{u}} f",
            )
            _eval(out, [r], point, "scalar")
    elif op in VECTOR_OPS:
        Fv = [parse(c) for c in (F or [])]
        if len(Fv) != 3:
            raise CalcError("Medan vektor butuh 3 komponen (P, Q, R).", "err.vec3")
        out["input"] = fmt_vec(Fv)
        out["input_latex"] = to_latex_vec(Fv)
        if op == "divergence":
            r = divergence(Fv)
            out.update(
                kind="scalar",
                result=fmt(r),
                latex=to_latex(r),
                label="∇·F",
                label_latex="\\nabla \\cdot \\mathbf{F}",
            )
            _eval(out, [r], point, "scalar")
        elif op == "curl":
            r = curl(Fv)
            out.update(
                kind="vector",
                result=fmt_vec(r),
                latex=to_latex_vec(r),
                label="∇×F",
                label_latex="\\nabla \\times \\mathbf{F}",
            )
            _eval(out, r, point, "vector")
        else:
            J = jacobian(Fv)
            out.update(
                kind="matrix",
                result=[fmt_vec(row) for row in J],
                latex=[to_latex_vec(row) for row in J],
                label="J(F)",
                label_latex="J(\\mathbf{F})",
            )
            if point:
                out["at_point"] = [[at_point(c, point) for c in row] for row in J]
    else:
        raise CalcError("Operasi tidak dikenal.", "err.op_unknown")
    return out


def _eval(out, exprs, point, kind):
    if not point:
        return
    vals = [at_point(e, point) for e in exprs]
    out["at_point"] = vals[0] if kind == "scalar" else vals


# ------------------------------------------------------------- graph data
def surface(f, xr, yr, n):
    fx = parse(f, allowed=(X, Y))
    n = max(10, min(int(n), 120))
    xs = np.linspace(xr[0], xr[1], n)
    ys = np.linspace(yr[0], yr[1], n)
    gx, gy = np.meshgrid(xs, ys)
    z = num(fx, gx, gy).reshape(gx.shape)
    zl = [[None if not np.isfinite(v) else float(v) for v in row] for row in z]
    return {"x": xs.tolist(), "y": ys.tolist(), "z": zl, "expr": fmt(fx)}


def field(F, rng, n):
    Fv = [parse(c) for c in F]
    if len(Fv) != 3:
        raise CalcError("Medan vektor butuh 3 komponen.", "err.vec3")
    n = max(2, min(int(n), 9))
    ax = np.linspace(rng[0], rng[1], n)
    gx, gy, gz = (a.ravel() for a in np.meshgrid(ax, ax, ax))
    u, v, w = (num(c, gx, gy, gz) for c in Fv)
    ok = np.isfinite(u) & np.isfinite(v) & np.isfinite(w)
    return {k: arr[ok].tolist() for k, arr in
            dict(x=gx, y=gy, z=gz, u=u, v=v, w=w).items()}


def curve(r, trange, n):
    comps = [parse(c, allowed=(T,)) for c in r]
    if len(comps) != 3:
        raise CalcError("Kurva butuh 3 komponen x(t), y(t), z(t).", "err.curve3")
    n = max(10, min(int(n), 2000))
    t = np.linspace(trange[0], trange[1], n)
    xs, ys, zs = (num_t(c, t) for c in comps)
    return {"x": clean(xs), "y": clean(ys), "z": clean(zs)}
