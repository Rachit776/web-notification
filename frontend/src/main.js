import './style.css';
import { requestNotificationPermission, getFCMToken, onMessageListener } from './firebase';

const subscribeButton = document.getElementById('subscribeBtn');
const statusText = document.getElementById('status');

const API_URL = '/api';

let isSubscribed = localStorage.getItem('fcmToken') !== null;
updateButtonState();

function updateButtonState() {
    if (isSubscribed) {
        subscribeButton.textContent = 'Unsubscribe';
        subscribeButton.classList.add('unsubscribe');
        statusText.textContent = 'You are subscribed to notifications';
    } else {
        subscribeButton.textContent = 'Subscribe';
        subscribeButton.classList.remove('unsubscribe');
        statusText.textContent = 'You are not subscribed to notifications';
    }
    subscribeButton.disabled = false;
}

async function registerServiceWorker() {
    try {
        const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
        return registration;
    } catch (err) {
        console.error('Service worker registration failed:', err);
        throw err;
    }
}

async function registerTokenWithBackend(token, unsubscribe = false) {
    try {
        const response = await fetch(`${API_URL}/devices/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                fcm_token: token,
                unsubscribe: unsubscribe 
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to register token with backend');
        }

        return await response.json();
    } catch (err) {
        console.error('Error with token operation:', err);
        throw err;
    }
}

async function unsubscribeFromNotifications() {
    try {
        subscribeButton.disabled = true;
        statusText.textContent = 'Unsubscribing...';

        const token = localStorage.getItem('fcmToken');
        if (token) {
            await registerTokenWithBackend(token, true);
            localStorage.removeItem('fcmToken');
        }

        // Unregister service worker
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration) {
            await registration.unregister();
        }

        isSubscribed = false;
        updateButtonState();
    } catch (err) {
        console.error('Error unsubscribing from notifications:', err);
        statusText.textContent = `Error: ${err.message}`;
        subscribeButton.disabled = false;
    }
}

async function subscribeToNotifications() {
    try {
        subscribeButton.disabled = true;
        statusText.textContent = 'Requesting permission...';

        await registerServiceWorker();
        await requestNotificationPermission();
        
        statusText.textContent = 'Getting FCM token...';
        const token = await getFCMToken();

        statusText.textContent = 'Registering with backend...';
        await registerTokenWithBackend(token);

        // Save token to localStorage
        localStorage.setItem('fcmToken', token);
        isSubscribed = true;
        updateButtonState();
    } catch (err) {
        console.error('Error subscribing to notifications:', err);
        statusText.textContent = `Error: ${err.message}`;
        subscribeButton.disabled = false;
    }
}

// Handle incoming messages when the app is in the foreground
onMessageListener()
    .then((payload) => {
        console.log('Received foreground message:', payload);
        // Only show notification if the app is not focused
        if (!document.hasFocus()) {
            new Notification(payload.notification.title, {
                body: payload.notification.body,
                icon: payload.notification.image,
            });
        }
    })
    .catch((err) => console.error('Error receiving message:', err));

// Add visibility change handler to track app focus
document.addEventListener('visibilitychange', () => {
    console.log('Visibility state:', document.visibilityState);
});

// Handle subscribe/unsubscribe button click
subscribeButton.addEventListener('click', async () => {
    if (isSubscribed) {
        await unsubscribeFromNotifications();
    } else {
        await subscribeToNotifications();
    }
}); 