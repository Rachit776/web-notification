importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js');

// Service worker configuration
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Initialize Firebase with configuration from the main app
firebase.initializeApp({
    apiKey: 'AIzaSyA0m9uYU1Qt2DcS0u7i2m3vNxHtWpUGNp0',
    authDomain: 'web-notification-system-c1613.firebaseapp.com',
    projectId: 'web-notification-system-c1613',
    storageBucket: 'web-notification-system-c1613.firebasestorage.app',
    messagingSenderId: '1056237836137',
    appId: '1:1056237836137:web:31d834f35f99147a480ff8'
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage(async (payload) => {
    console.log('Received background message:', payload);

    // Check if any window is focused
    const windows = await clients.matchAll({
        type: 'window',
        includeUncontrolled: true
    });
    
    const isAnyWindowFocused = windows.some(window => window.focused);
    
    // Only show notification if no window is focused
    if (!isAnyWindowFocused) {
        const notificationTitle = payload.notification.title;
        const notificationOptions = {
            body: payload.notification.body,
            icon: payload.notification.image,
            data: payload.data,
            actions: payload.data && payload.data.action_url ? [
                {
                    action: 'open_url',
                    title: 'Open',
                    icon: '/icons/open.png'
                }
            ] : undefined
        };

        return self.registration.showNotification(notificationTitle, notificationOptions);
    }
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'open_url' && event.notification.data.action_url) {
        clients.openWindow(event.notification.data.action_url);
    } else {
        // If no specific action, focus or open the app
        event.waitUntil(
            clients.matchAll({
                type: 'window',
                includeUncontrolled: true
            }).then(clientList => {
                for (const client of clientList) {
                    if (client.url === '/' && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow('/');
                }
            })
        );
    }
}); 