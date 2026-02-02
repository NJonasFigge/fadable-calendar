self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('fetch', event => {
  // Einfach weiterreichen – kein Cache fürs PoC nötig
});