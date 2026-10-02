# アクセント道場

声劇向け・標準語イントネーション練習アプリ（iPhone Safari想定）。

- `sentences.txt` … 練習文（`レベル|文1|文2...`）
- `build.py` … 読み・ルビ・アクセントを計算して `index.html` を生成（要 `pip install pyopenjtalk`）
- `template.html` … 画面のひな形
- `VERSION` … バージョン番号

更新手順: `sentences.txt` を編集 → `VERSION` を上げる → `python build.py` → commit & push
