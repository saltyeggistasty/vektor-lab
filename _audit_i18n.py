# -*- coding: utf-8 -*-
"""Dump ELEMEN use per tool (key useN + literal fallback) -> _use_elems.json"""
import io, json, re

src = io.open("static/tools.js", encoding="utf-8").read()
sim_m = re.search(r"SIM_IDS\s*=\s*new Set\(\[([^\]]*)\]\)", src)
sim_ids = set(re.findall(r'"([a-z0-9_]+)"', sim_m.group(1))) if sim_m else set()


def scan_block(s, open_idx):
    depth, i, in_str, esc = 0, open_idx, False, False
    while i < len(s):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c in "[{":
                depth += 1
            elif c in "]}":
                depth -= 1
                if depth == 0:
                    return s[open_idx:i + 1], i + 1
        i += 1
    return None, -1


def top_elems(body):
    elems, depth, cur, in_str, esc = [], 0, "", False, False
    for c in body:
        if in_str:
            cur += c
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
            cur += c
        elif c in "[{":
            depth += 1
            cur += c
        elif c in "]}":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            elems.append(cur)
            cur = ""
        else:
            cur += c
    if cur.strip():
        elems.append(cur)
    return [e.strip() for e in elems if e.strip()]


t0 = src.find("const TOOLS = {")
body, _ = scan_block(src, src.find("{", t0))
i, out = 1, {}
while i < len(body):
    m = re.compile(r'([a-z0-9_]+):\s*\{').search(body, i)
    if not m:
        break
    tid = m.group(1)
    blk, after = scan_block(body, body.find("{", m.start()))
    j = blk.find("use:")
    if j != -1:
        b = blk.find("[", j)
        ubody, _ = scan_block(blk, b)
        for k, el in enumerate(top_elems(ubody), 1):
            el = el.strip()
            if el.startswith('"') and el.endswith('"'):
                el = el[1:-1]
            grp = "sims" if tid in sim_ids else "tools"
            out[grp + "." + tid + ".use" + str(k)] = el
    i = after

io.open("_use_elems.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print(len(out), "elemen")
for k, v in out.items():
    print(k, "=>", v[:110])
