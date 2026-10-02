"""ホーム画面用アイコンを生成（朱色の地に「道」、高低の線）。"""
from PIL import Image, ImageDraw, ImageFont
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def icon(size, path, pad=0.0):
    S = 1024
    im = Image.new("RGB", (S, S), "#c2412d")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(BOLD, int(S * 0.48 * (1 - pad)), index=0)  # JP
    d.text((S / 2, S * (0.41 + pad * 0.05)), "道", font=f, fill="#fffdf8", anchor="mm")
    # 高低アクセントの線（低→高→低）
    y_lo, y_hi = S * (0.86 - pad * 0.25), S * (0.79 - pad * 0.25)
    xs = [S * (0.30 + pad * 0.1), S * 0.43, S * 0.57, S * (0.70 - pad * 0.1)]
    pts = [(xs[0], y_lo), (xs[1], y_hi), (xs[2], y_hi), (xs[3], y_lo)]
    d.line(pts, fill="#f6d9a8", width=int(S * 0.028), joint="curve")
    for p in pts:
        r = S * 0.03
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill="#f6d9a8")
    im.resize((size, size), Image.LANCZOS).save(path)

icon(180, "icons/apple-touch-icon.png")
icon(192, "icons/icon-192.png")
icon(512, "icons/icon-512.png")
icon(512, "icons/icon-maskable-512.png", pad=0.18)
print("icons ok")
