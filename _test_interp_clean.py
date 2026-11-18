# -*- coding: utf-8 -*-
"""Tes guardrail reasoning interpreter (kasus nyata dr screenshot pemilik)."""
import physics as ph

# kasus 1: bocoran persis kayak screenshot (reasoning + draf berkutip)
leak = (
    "We need to produce a JSON with key \"tafsiran\" containing the "
    "interpretation in Indonesian, plain text, 3-6 sentences, casual but "
    "precise, no markdown. Must follow rules: first sentence must be the "
    "final interpretation. Maybe mention hemisphere approximation? "
    "Sentence 1: \"Fluks total -4.80 N\u00b7m\u00b2/C berarti medan listrik "
    "seragam 5 N/C yang mengarah diagonal (1,1,1) keluar lebih banyak sisi "
    "bawah permukaan bergelombang z = sin(x+y) daripada masuk.\" "
    "That mentions flux number. Sentence 2: \"Kalau kita pakai hukum Gauss "
    "formal, muatan yan"
)
out = ph._clean_interp(leak)
print("kasus1 ->", out[:90] if out else "(kosong -> retry model lain)")

# kasus 2: jawaban bersih harus lolos UTUH
good = ("Fluks total 2,32 N\u00b7m\u00b2/C itu aliran medan listrik menembus "
        "permukaan bergelombang. Seperti hujan lewat jendela kaca miring, "
        "lebih banyak tetes yang menembus sisi bawah.")
out2 = ph._clean_interp(good)
assert out2 == " ".join(good.split()), out2
print("kasus2 OK (bersih utuh)")

# kasus 3: lamunan tunggal tanpa jawaban -> kosong (frontend nampung gagal,
# rotasi model berikutnya dicoba)
out3 = ph._clean_interp("Wait, is this possible? Maybe. Perhaps the user wants JSON.")
print("kasus3 ->", repr(out3))

# kasus 4: campuran — lamunan di awal, jawaban di tengah
mix = ("Let me analyze the data: flux 2.32 N\u00b7m\u00b2/C. "
       "Fluks 2,32 N\u00b7m\u00b2/C artinya medan menembus permukaan "
       "bergelombang seperti hujan di kaca.")
out4 = ph._clean_interp(mix)
assert "Let me" not in out4 and "Fluks 2,32" in out4, out4
print("kasus4 OK ->", out4[:70])
