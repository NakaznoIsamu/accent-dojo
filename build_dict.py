"""アクセント辞書データ dict.json を作る。

元データ: NAIST Japanese Dictionary (naist-jdic.csv, OpenJTalk同梱版)
  取得: git clone --depth 1 --filter=blob:none --sparse https://github.com/r9y9/open_jtalk.git
        git -C open_jtalk sparse-checkout set src/mecab-naist-jdic
使い方: python build_dict.py <naist-jdic.csv のパス>

出力形式: [[表記, 読み(ひらがな), アクセント型, 種別(0=名詞 1=固有名詞 2=その他)], ...]
"""
import csv
import json
import re
import sys

POS_KEEP = {"名詞", "動詞", "形容詞", "副詞", "感動詞", "連体詞", "接続詞"}
KANA = re.compile(r"^[ァ-ヶー]+$")


def kata2hira(s: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def main(path: str):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.reader(f):
            pos, sub = r[4], r[5]
            if pos not in POS_KEEP or sub == "数":
                continue
            if r[0] != r[10]:  # 活用形は除き、辞書形（終止形）だけ
                continue
            read, acc = r[11], r[13]
            if not KANA.match(read) or "/" not in acc:
                continue
            a = acc.split("/")[0]
            if not a.isdigit():
                continue
            key = (r[0], kata2hira(read), int(a))
            kind = 1 if sub == "固有名詞" else (0 if pos == "名詞" else 2)
            # 一般名詞と固有名詞の両方にあれば一般名詞扱い
            rows[key] = min(rows.get(key, 9), kind)
    data = [[s, rd, a, p] for (s, rd, a), p in sorted(rows.items(), key=lambda x: (x[1], x[0][1], x[0][0]))]
    with open("dict.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(data)} 語を書き出しました（うち固有名詞 {sum(d[3] == 1 for d in data)} 語）")


if __name__ == "__main__":
    main(sys.argv[1])
