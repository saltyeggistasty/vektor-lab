# -*- coding: utf-8 -*-
"""Reproduce: bentuk getValue pasca-paste/tinkering -> error apa."""
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

VARIANTS = [
    ("asli", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x\bigm{|}_{x=1}"),
    ("bar hilang (paste)", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x_{x=1}"),
    ("bar+exponent (tinker)", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x^2_{x=1}"),
    ("bigm hilang (tinker)", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x{|}_{x=1}"),
    ("spasi ditambah", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2} x _{x=1}"),
    ("pipe doang", r"\dfrac{\mathrm{d}^2}{\mathrm{d}x^2}x|_{x=1}"),
]
for label, la in VARIANTS:
    try:
        marker = conv(la)
    except Exception as e:
        print(f"{label:26s} conv-ERR {e}"); continue
    if marker.startswith("__NABLA_ERR__"):
        print(f"{label:26s} -> SENTINEL {marker[12:]}"); continue
    if not marker.startswith("__NABLA_OP__"):
        print(f"{label:26s} -> PLAIN {marker[:60]!r}")
        try:
            r = mathlab.tool_integral({"expr": marker, "mode": "auto"})
            print(f"{'':26s}    backend: {r.get('plain')}")
        except mathlab.LabError as e:
            print(f"{'':26s}    backend-ERR: {e.key} {str(e)[:60]}")
        continue
    opd = json.loads(marker[12:])
    try:
        r = mathlab.tool_integral({"op_data": opd, "expr": "", "mode": "auto"})
        print(f"{label:26s} -> {r.get('plain')}  [op={opd['op']}]")
    except mathlab.LabError as e:
        print(f"{label:26s} -> backend-ERR {e.key}: {str(e)[:70]}")
    except Exception as e:
        print(f"{label:26s} -> CRASH {type(e).__name__}: {str(e)[:80]}")
