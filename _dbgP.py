# -*- coding: utf-8 -*-
import io, sys, json, subprocess, tempfile, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
js = open(os.path.join(ROOT, "test_integral_tool.py"), encoding="utf-8").read()
s0 = js.index('_NODE_JS = r"""') + len('_NODE_JS = r"""')
s1 = js.index('"""', s0)
node_code = js[s0:s1]

def conv(la):
    f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
    f.write(node_code); f.close()
    try:
        r = subprocess.run(["node", f.name, os.path.join(ROOT, "static", "tools.js"),
                            json.dumps({"la": la, "uneval": True})],
                           capture_output=True, text=True, encoding="utf-8")
        return json.loads(r.stdout)["out"]
    finally:
        os.unlink(f.name)

def run_case(la, mode="auto", extra=None):
    plain = conv(la)
    data = {"expr": plain, "mode": mode}
    if plain.startswith("__NABLA_OP__"):
        data["op_data"] = json.loads(plain[12:])
        data["expr"] = ""
    if extra:
        data.update(extra)
    return mathlab.tool_integral(data), plain

for la, mode, extra in [
    (r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x\bigm{|}_{x=1}", "auto", None),
    (r"\frac{d}{dx} x^3 \bigm{|}_{x=2}", "auto", None),
    (r"\prod_{i=1}^n x_i", "auto", None),
    (r"\int e^x\sin x\,dx", "indef", None),
    (r"\int x\arctan x\,dx", "indef", None),
    (r"\int_0^{\pi}x\sin x\,dx", "def", None),
]:
    try:
        d, plain = run_case(la, mode, extra)
        print(repr(la)[:55], "->", d.get("plain"), "|", [r[1] for r in d["rows"]])
    except Exception as e:
        print(repr(la)[:55], "-> ERR", type(e).__name__, str(e)[:90])

try:
    r = mathlab.run_tool("integral", {"expr": "n", "mode": "prod", "a": "1", "b": "3"})
    print("prod mode n 1..3 ->", r.get("plain"))
except Exception as e:
    print("prod mode ERR", e)
