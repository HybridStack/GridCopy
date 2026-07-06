const CACHE = "gridcopy-v1";
const CDN_CACHE = "gridcopy-cdn-v1";
const STATIC = [
  ".",
  "index.html",
  "manifest.json",
  "css/style.css",
  "js/app.js",
  "icons/icon.svg",
];
const CDN_URLS = [
  "https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      await cache.addAll(STATIC);
      const cdn = await caches.open(CDN_CACHE);
      for (const url of CDN_URLS) {
        try {
          const r = await fetch(url);
          if (r.ok) cdn.put(url, r);
        } catch (_) {}
      }
      await self.skipWaiting();
    })()
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(clients.claim());
  e.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => k !== CACHE && k !== CDN_CACHE)
          .map((k) => caches.delete(k))
      );
    })()
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (CDN_URLS.some((u) => e.request.url.startsWith(u))) {
    e.respondWith(networkFirst(e.request, CDN_CACHE));
    return;
  }
  if (STATIC.some((p) => url.pathname.endsWith(p) || url.pathname === "/")) {
    e.respondWith(cacheFirst(e.request, CACHE));
    return;
  }
  e.respondWith(networkFirst(e.request, CACHE));
});

async function cacheFirst(req, cacheName) {
  const cached = await caches.match(req);
  if (cached) return cached;
  try {
    const res = await fetch(req);
    if (res.ok) {
      const cache = await caches.open(cacheName);
      cache.put(req, res.clone());
    }
    return res;
  } catch {
    return new Response("Offline", { status: 503 });
  }
}

async function networkFirst(req, cacheName) {
  try {
    const res = await fetch(req);
    if (res.ok) {
      const cache = await caches.open(cacheName);
      cache.put(req, res.clone());
    }
    return res;
  } catch {
    const cached = await caches.match(req);
    return cached || new Response("Offline", { status: 503 });
  }
}
