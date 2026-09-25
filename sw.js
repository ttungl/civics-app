/* Civics service worker.
 * To publish an update: change VERSION below (e.g. 1.0.1), then upload.
 * Browsers see the changed file, install the new version, and remove the old cache. */
const VERSION = '1.3.0';
const CACHE = 'civics-' + VERSION;
// Recorded voices live in their own cache so app updates don't delete them.
// Change AUDIO_CACHE only after re-recording clips (tools/tts/generate_audio.py).
const AUDIO_CACHE = 'n400-audio-1';
const ASSETS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'favicon.png',
  'logo.webp',
  'logo-clear.webp',
  'logo-clear-dark.webp',
  'logo-mark.webp',
  'logo-wordmark.webp',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png',
  'icon-maskable-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(ASSETS.map((url) => new Request(url, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => (k.startsWith('civics-') && k !== CACHE) || (k.startsWith('n400-audio-') && k !== AUDIO_CACHE)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function timeout(ms) {
  return new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms));
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Pages: try the network first (fresh content), fall back to the cached copy offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      // no-cache: always ask the server (a quick 304 if unchanged), so updates show on the next visit.
      Promise.race([fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }), timeout(4000)])
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put('index.html', copy));
          }
          return res;
        })
        .catch(() => caches.match('index.html').then((r) => r || caches.match('./')))
    );
    return;
  }

  // Recorded voice clips: cache first, in the long-lived audio cache.
  if (url.pathname.includes('/audio/')) {
    event.respondWith(
      caches.open(AUDIO_CACHE).then((cache) => cache.match(req).then((hit) => hit || fetch(req).then((res) => {
        if (res && res.status === 200) cache.put(req, res.clone());
        return res;
      })))
    );
    return;
  }

  // Everything else: cache first, then network (and remember it).
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        if (res && res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      });
    })
  );
});
