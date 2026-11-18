# -*- coding: utf-8 -*-
"""Verifikasi pasca-inject: semua key SRC ada di 7 JSON + nilainya masuk akal."""
import io, json
import _add_use_keys as gen   # reuse SRC + REPL (tanpa efek samping selain cetak inject)

LANGS = ["indonesia", "english", "melayu", "russia", "ukraina", "irish", "arab"]
ok = True
for lang in LANGS:
    d = json.load(io.open(f"i18n/{lang}.json", encoding="utf-8"))

    def get(dd, path):
        for p in path.split("."):
            if not isinstance(dd, dict) or p not in dd:
                return None
            dd = dd[p]
        return dd

    miss = [k for k in gen.SRC if get(d, k) is None]
    if miss:
        ok = False
        print(lang, "MASIH KURANG:", miss[:10])
    # sampel: pastikan terjemahanRussia bener2 berubah dr literal Indonesia
    if lang == "russia":
        v = get(d, "tools.gfield.use2")
        assert "красный" in v, v
        v2 = get(d, "sims.skepler.use1")
        assert "Кеплера" in v2, v2
        v3 = get(d, "tools.stats.use2")
        assert "медиана" in v3, v3
    if lang == "arab":
        v = get(d, "tools.gfield.use2")
        assert "اسحب" in v, v
    if lang == "english":
        v = get(d, "tools.schwartz.use2")
        assert "time dilation" in v, v
    print(lang, "OK |", "contoh:", get(d, "tools.gfield.use2").encode("utf-8")[:60])

# pastikan key lain gak hilang: hitung total key vs sebelum inject tidak tersimpan,
# tapi minimal meta tiap bahasa masih ada
for lang in LANGS:
    d = json.load(io.open(f"i18n/{lang}.json", encoding="utf-8"))
    assert "meta" in d and "name" in d["meta"], lang
print("VALIDASI", "LULUS" if ok else "GAGAL")
