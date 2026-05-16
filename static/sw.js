// Service Worker — 오프라인 캐싱 + 정적 자산 최적화
const VERSION = 'saju-v1';
const STATIC_CACHE = `${VERSION}-static`;
const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(STATIC_CACHE).then(c => c.addAll(STATIC_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k.startsWith('saju-') && !k.startsWith(VERSION)).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // 광고/추적 요청은 그냥 통과
  if (url.hostname.includes('googlesyndication') ||
      url.hostname.includes('facebook') ||
      url.hostname.includes('google-analytics') ||
      url.hostname.includes('googletagmanager')) return;
  // 정적 자산: cache-first
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached =>
        cached || fetch(e.request).then(resp => {
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(STATIC_CACHE).then(c => c.put(e.request, clone));
          }
          return resp;
        })
      )
    );
    return;
  }
  // HTML: network-first with offline fallback
  if (e.request.mode === 'navigate' || (e.request.headers.get('accept') || '').includes('text/html')) {
    e.respondWith(
      fetch(e.request).catch(() => caches.match(e.request) || caches.match('/'))
    );
  }
});
