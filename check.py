"""sentences.txt の各文の読みとアクセント型を表示して目視チェックするための補助スクリプト。"""
import pyopenjtalk
from build import pitch_line, kata2hira

for line in open("sentences.txt", encoding="utf-8"):
    if not line.strip() or line.startswith("#"):
        continue
    lv, *ss = line.strip().split("|")
    for s in ss:
        nj = pyopenjtalk.run_frontend(s)
        print(lv, s)
        print("   ", " ".join(f"{n['string']}[{n['read']}:{n['acc']}]" for n in nj if n["string"] not in "。、"))
        print("   ", pitch_line(s, kata2hira("".join(n["read"] for n in nj))))
