import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { page } from '$app/stores';

// Add a log at the very top to confirm this file version is loaded
console.log('auth.js: File loaded. Version with debug logs.');

export const isAuthenticated = writable(false);
export const user = writable(null);
export const accessToken = writable(null);

// Initialize store from localStorage if in browser
if (browser) {
    const storedUser = localStorage.getItem('user');
    const storedAccessToken = localStorage.getItem('accessToken');

    if (storedUser && storedAccessToken) {
        user.set(JSON.parse(storedUser));
        accessToken.set(storedAccessToken);
        isAuthenticated.set(true);
        console.log('auth.js: Initialized from localStorage. isAuthenticated:', get(isAuthenticated));
    } else {
        console.log('auth.js: No user/token in localStorage. isAuthenticated:', get(isAuthenticated));
    }

    // Subscribe to page changes to handle redirects for protected routes
    page.subscribe(($page) => {
        console.log('auth.js: page.subscribe triggered. $page:', $page);

        // Add a safety check for $page.url
        if (!$page || !$page.url || typeof $page.url.pathname === 'undefined') {
            console.warn('auth.js: Svelte $page.url is not yet defined or has unexpected structure. Skipping auth check.');
            return; // Exit if $page.url is not ready
        }

        const publicRoutes = ['/login', '/register'];
        const currentPath = $page.url.pathname;
        const currentIsAuthenticated = get(isAuthenticated);

        console.log(`auth.js: currentPath: ${currentPath}, isAuthenticated: ${currentIsAuthenticated}, isPublicRoute: ${publicRoutes.includes(currentPath)}`);

        // If the user is NOT authenticated AND the current route is NOT a public route,
        // then redirect to login.
        if (!currentIsAuthenticated && !publicRoutes.includes(currentPath)) {
            console.log('auth.js: Redirecting to /login due to unauthenticated access to protected route.');
            // Prevent infinite loops if already on login/register or if it's the root path
            if (currentPath !== '/' && currentPath !== '/login') {
                goto('/login');
            } else if (currentPath === '/') {
                goto('/login');
            }
        } else if (currentIsAuthenticated && publicRoutes.includes(currentPath)) {
            // OPTIONAL: If authenticated and trying to access login/register, redirect to dashboard
            console.log('auth.js: Authenticated user trying to access public route. Redirecting to /dashboard.');
            goto('/dashboard');
        } else {
            console.log('auth.js: No redirection needed for current path and auth state.');
        }
    });
}

export async function login(userInfo, tokenValue) {
    user.set(userInfo);
    accessToken.set(tokenValue);
    isAuthenticated.set(true);
    if (browser) {
        localStorage.setItem('user', JSON.stringify(userInfo));
        localStorage.setItem('accessToken', tokenValue);
    }
    console.log('auth.js: User logged in. isAuthenticated:', get(isAuthenticated));
}

export function logout() {
    user.set(null);
    accessToken.set(null);
    isAuthenticated.set(false);
    if (browser) {
        localStorage.removeItem('user');
        localStorage.removeItem('accessToken');
    }
    console.log('auth.js: User logged out. isAuthenticated:', get(isAuthenticated));
}

export const UserRole = {
    REPORTER: 'reporter',
    MAINTAINER: 'maintainer',
    ADMIN: 'admin'
};