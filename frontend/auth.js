/**
 * AUTH.JS — Client-side authentication handler for ResourcePro
 * Manages JWT storage, API calls, token refresh, and auth state.
 */

const AUTH_API = '/api/auth';

const Auth = {
    // ─── TOKEN MANAGEMENT ─────────────────────────────────────────
    getAccessToken() {
        return localStorage.getItem('rp_access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('rp_refresh_token');
    },

    getUser() {
        const raw = localStorage.getItem('rp_user');
        try { return raw ? JSON.parse(raw) : null; } catch { return null; }
    },

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('rp_access_token', accessToken);
        if (refreshToken) localStorage.setItem('rp_refresh_token', refreshToken);
    },

    setUser(user) {
        localStorage.setItem('rp_user', JSON.stringify(user));
    },

    clearAuth() {
        localStorage.removeItem('rp_access_token');
        localStorage.removeItem('rp_refresh_token');
        localStorage.removeItem('rp_user');
    },

    isLoggedIn() {
        return !!this.getAccessToken() && !!this.getUser();
    },

    getUserRole() {
        const user = this.getUser();
        return user ? user.role : null;
    },

    // ─── AUTH HEADERS ─────────────────────────────────────────────
    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = this.getAccessToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    },

    // ─── API CALLS ────────────────────────────────────────────────
    async register(name, email, password, role) {
        try {
            const res = await fetch(`${AUTH_API}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, role })
            });
            const data = await res.json();
            if (data.status === 'success') {
                this.setTokens(data.access_token, data.refresh_token);
                this.setUser(data.user);
            }
            return data;
        } catch (err) {
            return { status: 'error', message: 'Network error. Please try again.' };
        }
    },

    async login(email, password, rememberMe = false) {
        try {
            const res = await fetch(`${AUTH_API}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, remember_me: rememberMe })
            });
            const data = await res.json();
            if (data.status === 'success') {
                this.setTokens(data.access_token, data.refresh_token);
                this.setUser(data.user);
            }
            return data;
        } catch (err) {
            return { status: 'error', message: 'Network error. Please try again.' };
        }
    },

    async logout() {
        try {
            await fetch(`${AUTH_API}/logout`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ refresh_token: this.getRefreshToken() })
            });
        } catch (e) { /* ignore logout errors */ }
        this.clearAuth();
        window.location.href = '/login.html';
    },

    async refreshToken() {
        try {
            const res = await fetch(`${AUTH_API}/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: this.getRefreshToken() })
            });
            const data = await res.json();
            if (data.status === 'success') {
                this.setTokens(data.access_token);
                this.setUser(data.user);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    },

    async getProfile() {
        try {
            const res = await fetch(`${AUTH_API}/profile`, {
                headers: this.getHeaders()
            });
            if (res.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    const retry = await fetch(`${AUTH_API}/profile`, { headers: this.getHeaders() });
                    return await retry.json();
                }
                this.clearAuth();
                window.location.href = '/login.html';
                return null;
            }
            return await res.json();
        } catch {
            return { status: 'error', message: 'Network error' };
        }
    },

    async getActivity(limit = 20) {
        try {
            const res = await fetch(`${AUTH_API}/activity?limit=${limit}`, {
                headers: this.getHeaders()
            });
            return await res.json();
        } catch {
            return { status: 'error', message: 'Network error' };
        }
    },

    async forgotPassword(email) {
        try {
            const res = await fetch(`${AUTH_API}/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            return await res.json();
        } catch {
            return { status: 'error', message: 'Network error' };
        }
    },

    async resetPassword(token, newPassword) {
        try {
            const res = await fetch(`${AUTH_API}/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password: newPassword })
            });
            return await res.json();
        } catch {
            return { status: 'error', message: 'Network error' };
        }
    },

    // ─── AUTH-PROTECTED FETCH ─────────────────────────────────────
    async authFetch(url, options = {}) {
        options.headers = { ...this.getHeaders(), ...(options.headers || {}) };
        let res = await fetch(url, options);
        if (res.status === 401) {
            const refreshed = await this.refreshToken();
            if (refreshed) {
                options.headers = { ...this.getHeaders(), ...(options.headers || {}) };
                res = await fetch(url, options);
            } else {
                this.clearAuth();
                window.location.href = '/login.html';
                return null;
            }
        }
        return res;
    },

    // ─── ROUTE PROTECTION ─────────────────────────────────────────
    requireAuth(allowedRoles = null) {
        if (!this.isLoggedIn()) {
            window.location.href = '/login.html';
            return false;
        }
        if (allowedRoles && !allowedRoles.includes(this.getUserRole())) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }
};

// Make Auth globally available
window.Auth = Auth;
