# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"G:\vektor-lab(1)\vektor-lab"
sys.path.insert(0, ROOT)
import mathlab
from test_benchmark import conv

INPUTS = [
 (r"\lim_{x\to 0}\frac{e^x-1-x-\frac{x^2}{2}}{x^3}", "L01"),
 (r"\frac{d}{dx}\sqrt{1+\sin^2 x}", "D08"),
 (r"\frac{d}{dx}\arctan\left(\frac{x}{\sqrt{1-x^2}}\right)", "D05"),
 (r"\frac{d}{dx}\left(x^2y+\sin(xy)\right)", "D15"),
 (r"\frac{d}{dx}\left(x^2+1\right)^{\sin x}", "D06"),
 (r"\sum_{n=1}^{\infty}\frac{1}{n(n+1)}", "S05"),
 (r"\sum_{n=1}^{\infty}\frac{1}{n\,2^n}", "S10"),
 (r"\sum_{n=1}^{\infty}\frac{n}{2^n}", "S08"),
 (r"\int xe^x\,dx", "I01"),
 (r"\int_0^1 x^2e^x\,dx", "DI01"),
 (r"\int_0^1\frac{d}{dx}\left(x^3e^x\right)dx", "C01"),
]
for la, tag in INPUTS:
    try:
        plain = conv(la, uneval=True)
        print(f"{tag:6s} -> {plain[:110]}")
    except Exception as e:
        print(f"{tag:6s} -> CONV-ERR {e}")
