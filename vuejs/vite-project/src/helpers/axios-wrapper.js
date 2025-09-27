import { useAuthStore } from '@/stores/auth.store.js';
import axios from 'axios'

export const axiosWrapper = {
    get:    request('GET'),
    patch:  request('PATCH'),
    post:   request('POST'),
    put:    request('PUT'),
    delete: request('DELETE')
};

function request(method) {
    return (uri, body) => {
        let url = `${import.meta.env.VITE_API_URL}/${uri}`
        let headers = authHeader(url)
        if (body) {
            headers['Content-Type'] = 'application/json';
            body = JSON.stringify(body);
        }

        const data = axios({
            method: method,
            url: url,
            data: body,
            headers: headers
        }).then(response => {
        })
        .catch(response => {
            const { user, logout } = useAuthStore();
            const error = (response.data && response.data.detail) || response.statusText;
            console.error('Error creating item:', error);
            if ([401, 403].includes(response.status) && user) logout();
            throw new Error(error);
        });
        return data
    }
}

function authHeader(url) {
    // return auth header with jwt if user is logged in and request is to the api url
    const { user } = useAuthStore();
    const isLoggedIn = !!user?.token;
    const isApiUrl = url.startsWith(import.meta.env.VITE_API_URL);
    return (isLoggedIn && isApiUrl) ? { Authorization: `Bearer ${user.token}` } : {};
}
