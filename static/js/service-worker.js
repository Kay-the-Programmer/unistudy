// STRETCH GOAL: Service Worker for Offline Access
// This file would contain logic for caching materials for offline use.

// self.addEventListener('install', event => {
//   console.log('Service Worker: Installing...');
//   // Perform install steps, like caching static assets
//   event.waitUntil(
//     caches.open('zstudy-static-cache-v1').then(cache => {
//       return cache.addAll([
//         '/',
//         // Add other core assets like base.html, CSS, main JS
//       ]);
//     })
//   );
// });

// self.addEventListener('fetch', event => {
//   console.log('Service Worker: Fetching ', event.request.url);
//   // Respond with cached resources if available, or fetch from network
//   event.respondWith(
//     caches.match(event.request).then(response => {
//       return response || fetch(event.request);
//     })
//   );
// });

// self.addEventListener('message', event => {
//   // Handle messages from the main app, e.g., to cache a specific material
//   if (event.data.action === 'cache-material') {
//     // const materialUrl = event.data.url;
//     // caches.open('zstudy-materials-cache').then(cache => cache.add(materialUrl));
//   }
// });
