# -*- coding: utf-8 -*-
"""Update tools.poly.hint ke 7 bahasa: polinom ditulis utuh."""
import json, io

HINTS = {
    "english": "Type the whole polynomial p(x) above, e.g. x^2 - 5x + 6, then choose roots or factorisation. Operators like the definite integral are evaluated first automatically.",
    "indonesia": "Tulis polinom utuh p(x) di atas, mis. x^2 - 5x + 6, lalu pilih akar atau faktorisasi. Operasi seperti integral tentu dievaluasi dulu otomatis.",
    "melayu": "Tulis polinomial penuh p(x) di atas, cth. x^2 - 5x + 6, kemudian pilih punca atau pemfaktoran. Operasi seperti kamiran tentu dinilai dahulu secara automatik.",
    "russia": "Введите весь полином p(x) выше, напр. x^2 - 5x + 6, затем выберите корни или разложение. Операторы вроде определённого интеграла вычисляются сначала автоматически.",
    "ukraina": "Введіть увесь поліном p(x) вище, напр. x^2 - 5x + 6, потім оберіть корені або розкладання. Оператори типу певного інтеграла обчислюються спочатку автоматично.",
    "irish": "Cuir isteach an polynóim iomlán p(x) thuas, m.s. x^2 - 5x + 6, agus roghnaigh fréamhacha nó fachtóiriú. Déantar oibreán cosúil leis an tsuimiúchin comhtháite a mheas ar dtús go huathoibríoch.",
    "arab": "اكتب كامل متعدد الحدود p(x) أعلاه، مثل x^2 - 5x + 6، ثم اختر الجذور أو التحليل. يتم حساب المعاملات مثل التكامل المحدد تلقائياً أولاً.",
}

for lang, hint in HINTS.items():
    p = f"i18n/{lang}.json"
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    d.setdefault("tools", {}).setdefault("poly", {})["hint"] = hint
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(lang, "OK")
