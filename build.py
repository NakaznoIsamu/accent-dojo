"""sentences.txt から data.json を作り、index.html に埋め込むビルドスクリプト。

sentences.txt の書式:  レベル|文1|文2|...
"""
import json
import re
import pyopenjtalk

KANJI = re.compile(r"[\u4e00-\u9fff々〆ヵヶ]")


def kata2hira(s: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def split_okurigana(surface: str, reading: str):
    """「渡る/わたる」→ [("渡","わた"),("る",None)] のように送り仮名を分ける。"""
    pre = ""
    while surface and reading and surface[0] == reading[0] and not KANJI.match(surface[0]):
        pre += surface[0]
        surface, reading = surface[1:], reading[1:]
    post = ""
    while surface and reading and surface[-1] == reading[-1] and not KANJI.match(surface[-1]):
        post = surface[-1] + post
        surface, reading = surface[:-1], reading[:-1]
    parts = []
    if pre:
        parts.append([pre, None])
    if surface:
        parts.append([surface, reading if KANJI.search(surface) else None])
    if post:
        parts.append([post, None])
    return parts


def pitch_moras(text: str):
    """アクセント句ごとのモーラと高低（ステップ3で使用）。"""
    labels = pyopenjtalk.make_label(pyopenjtalk.run_frontend(text))
    phrases, cur, last = [], [], None
    for l in labels:
        p = re.search(r"\-(.*?)\+", l).group(1)
        if p in ("sil", "pau"):
            if cur:
                phrases.append(cur)
                cur, last = [], None
            continue
        a = re.search(r"/A:([\-\d]+)\+(\d+)\+(\d+)", l)
        a2 = int(a.group(2))
        acc = int(re.search(r"/F:\d+_(\d+)", l).group(1))
        hi = (acc == 0 and a2 > 1) or (acc == 1 and a2 == 1) or (acc > 1 and 1 < a2 <= acc)
        # 同じ句の中で a2 が減ったら新しいアクセント句
        if last is not None and a2 <= last[0] and a2 == 1:
            phrases.append(cur)
            cur = []
        if last is not None and a2 == last[0]:
            continue  # 子音→母音など同じモーラの続き
        cur.append(1 if hi else 0)
        last = (a2,)
    if cur:
        phrases.append(cur)
    return phrases


def build_line(text: str):
    tokens = []
    for n in pyopenjtalk.run_frontend(text):
        surf = n["string"]
        read = kata2hira(n["read"]) if n["read"] not in ("、", "。") else surf
        if KANJI.search(surf):
            tokens.extend(split_okurigana(surf, read))
        else:
            tokens.append([surf, None])
    reading = "".join(
        kata2hira(n["read"]) if n["read"] not in ("、", "。") else n["string"]
        for n in pyopenjtalk.run_frontend(text)
    )
    return {"text": text, "tokens": tokens, "reading": reading, "pitch": pitch_moras(text)}


def main():
    items = []
    for raw in open("sentences.txt", encoding="utf-8"):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        level, *lines = raw.split("|")
        items.append({"level": level, "lines": [build_line(t) for t in lines]})
    data = {"version": open("VERSION").read().strip(), "items": items}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    html = open("template.html", encoding="utf-8").read()
    html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    html = html.replace("__VERSION__", data["version"])
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{len(items)} 問を書き出しました (v{data['version']})")


if __name__ == "__main__":
    main()
