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


VOWEL_END = {"a", "i", "u", "e", "o", "A", "I", "U", "E", "O", "N", "cl"}
SMALL_KANA = set("ぁぃぅぇぉゃゅょゎ")


def label_morae(text: str):
    """OpenJTalkのラベルから、モーラごとの (高=1/低=0, アクセント句の先頭=1) を返す。"""
    out, cur = [], None
    for l in pyopenjtalk.make_label(pyopenjtalk.run_frontend(text)):
        p = re.search(r"\-(.*?)\+", l).group(1)
        if p in ("sil", "pau"):
            continue
        if cur is None:  # モーラの最初の音素で高低を決める
            a2 = int(re.search(r"/A:[\-\d]+\+(\d+)\+", l).group(1))
            acc = int(re.search(r"/F:\d+_(\d+)", l).group(1))
            hi = (acc == 0 and a2 > 1) or (acc == 1 and a2 == 1) or (acc > 1 and 1 < a2 <= acc)
            cur = (1 if hi else 0, 1 if a2 == 1 else 0)
        if p in VOWEL_END:  # 母音・撥音・促音でモーラが終わる
            out.append(cur)
            cur = None
    return out


def pitch_line(text: str, reading: str):
    """読み（ひらがな）をモーラに分け、各モーラに高低を付ける。
    戻り値: [[かな, 高低, 句頭], ..., ["、"], ...]。数が合わなければ None。"""
    morae = []
    for c in reading:
        if c in "、。":
            morae.append(c)
        elif c in SMALL_KANA and morae and morae[-1] not in "、。":
            morae[-1] += c
        else:
            morae.append(c)
    labels = label_morae(text)
    if len(labels) != sum(m not in "、。" for m in morae):
        return None
    res, i = [], 0
    for m in morae:
        if m in "、。":
            res.append([m])
        else:
            res.append([m, *labels[i]])
            i += 1
    return res


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
    pitch = pitch_line(text, reading)
    if pitch is None:
        print(f"  ※高低線を作れませんでした（読みとモーラ数が不一致）: {text}")
    return {"text": text, "tokens": tokens, "reading": reading, "pitch": pitch}


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
    sw = open("sw.template.js", encoding="utf-8").read().replace("__VERSION__", data["version"])
    with open("sw.js", "w", encoding="utf-8") as f:
        f.write(sw)
    print(f"{len(items)} 問を書き出しました (v{data['version']})")


if __name__ == "__main__":
    main()
