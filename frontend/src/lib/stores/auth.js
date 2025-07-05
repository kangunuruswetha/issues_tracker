import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Create stores
export const user = writable(null);
export const token = writable(null);
export const isAuthenticated = writable(false);

// Initialize stores from localStorage
if (browser) {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
        token.set(savedToken);
        user.set(JSON.parse(savedUser));
        isAuthenticated.set(true);
    }
}

// Subscribe to changes and update localStorage
if (browser) {
    token.subscribe(value => {
        if (value) {
            localStorage.setItem('token', value);
        } else {
            localStorage.removeItem('token');
        }
    });

    user.subscribe(value => {
        if (value) {
            localStorage.setItem('user', JSON.stringify(value));
        } else {
            localStorage.removeItem('user');
        }
    });
}

export function login(userdata, tokenData) {
    user.set(userdata);
    token.set(tokenData);
    isAuthenticated.set(true);
}

export function logout() {
    user.set(null);
    token.set(null);
    isAuthenticated.set(false);
    if (browser) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    }
}
