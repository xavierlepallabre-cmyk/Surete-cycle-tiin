/* Sûreté & Cycle TIIN — service worker
   Projet indépendant de Nucléa TIIN : préfixe de cache propre, portée limitée au dossier du site.
   VERSION est calculée par « python tools/version.py » à partir du contenu des fichiers :
   la lancer avant chaque publication (le test « python tests/test_site.py » le vérifie). */
const VERSION = 'c1fc6d0594';
const PREFIX = 'surete-cycle-tiin-';
const CACHE = PREFIX + VERSION;
const ASSETS = [
  './',
  './index.html',
  './amont.html',
  './rep1300.html',
  './lahague.html',
  './andra.html',
  './surete.html',
  './accidents.html',
  './manifest.json',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png'
];

/* Installation : tout est téléchargé depuis le serveur (jamais depuis le cache HTTP),
   pour ne pas mélanger des fichiers de deux versions. */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS.map(url => new Request(url, { cache: 'reload' }))))
  );
});

/* La nouvelle version ne s'active que lorsque l'utilisateur accepte la mise à jour. */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'ACTIVATE_UPDATE') self.skipWaiting();
});

/* Activation : suppression des anciennes versions de CE site uniquement. */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith(PREFIX) && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

/* Cache d'abord : le site fonctionne entièrement hors connexion. */
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(request, { ignoreSearch: true });
    if (hit) return hit;
    try {
      const response = await fetch(request);
      if (response.ok && url.pathname.startsWith(new URL(self.registration.scope).pathname)) cache.put(request, response.clone());
      return response;
    } catch (error) {
      if (request.mode === 'navigate') return (await cache.match('./index.html')) || Response.error();
      throw error;
    }
  })());
});
