// アクセント道場 Service Worker — v__VERSION__
// バージョンを上げるとキャッシュ名が変わり、新しい版に入れ替わる。
const CACHE = "accent-dojo-__VERSION__";
const FONT_CACHE = "accent-dojo-fonts";
const CORE = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icons/apple-touch-icon.png", "./icons/icon-192.png", "./icons/icon-512.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE && k !== FONT_CACHE).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("message", e => {
  if (e.data === "skipWaiting") self.skipWaiting();
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;

  // Google Fonts: 一度読んだら端末に保存（オフラインでも同じ字体で表示）
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(
      caches.open(FONT_CACHE).then(async c => {
        const hit = await c.match(e.request);
        if (hit) return hit;
        try {
          const res = await fetch(e.request);
          c.put(e.request, res.clone());
          return res;
        } catch { return Response.error(); }
      })
    );
    return;
  }

  if (url.origin !== location.origin) return;

  // 自分のファイル: 保存済みを即表示（電波なしでも動く）。更新はバージョン変更で。
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match("./index.html")))
  );
});
