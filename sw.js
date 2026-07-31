self.addEventListener('fetch', (event) => {
  // Pass-through fetch handler to satisfy PWA requirements
  event.respondWith(fetch(event.request));
});