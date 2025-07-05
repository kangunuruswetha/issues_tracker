import { get } from 'svelte/store';
import { token } from '$lib/stores/auth.js';
import { browser } from '$app/environment';

const API_BASE = browser ? '/api' : 'http://localhost:8000';

class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.status = status;
        this.data = data;
    }
}

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const currentToken = get(token);

    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    if (currentToken) {
        config.headers.Authorization = `Bearer ${currentToken}`;
    }

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(
                errorData.detail || `HTTP error! status: ${response.status}`,
                response.status,
                errorData
            );
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return response;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new ApiError('Network error', 0, { message: error.message });
    }
}

// Auth API
export const authApi = {
    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        return apiCall('/users/token', {
            method: 'POST',
            headers: {}, // Remove Content-Type for FormData
            body: formData
        });
    },

    async register(userData) {
        return apiCall('/users/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
};

// Issues API
export const issuesApi = {
    async getAll(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = `/issues${queryString ? `?${queryString}` : ''}`;
        return apiCall(endpoint);
    },

    async getById(id) {
        return apiCall(`/issues/${id}`);
    },

    async create(formData) {
        return apiCall('/issues/', {
            method: 'POST',
            headers: {}, // Remove Content-Type for FormData
            body: formData
        });
    },

    async update(id, data) {
        return apiCall(`/issues/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(id) {
        return apiCall(`/issues/${id}`, {
            method: 'DELETE'
        });
    },

    async getDashboardStats() {
        return apiCall('/issues/dashboard/stats');
    }
};

export { ApiError };
