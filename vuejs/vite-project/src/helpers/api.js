import { useAuthStore } from '@/stores/auth.store.js';
import axios from 'axios';
export const http = {
    get:    (path, config) => axiosObject().get(path, config),
    post:   (path, body)   => axiosObject().post(path, body),
    put:    (path, body)   => axiosObject().put(path, body),
    patch:  (path, body)   => axiosObject().patch(path, body),
    delete: (path)         => axiosObject().delete(path),
}

function axiosObject() {
    let headers = {}
    const authStore = useAuthStore();
    const isLoggedIn = !!authStore?.token;
    if (isLoggedIn) headers['Authorization'] = `Bearer ${authStore.token}`;
    headers['Content-Type'] = 'application/json';
    return axios.create({
        baseURL: import.meta.env.VITE_API_URL,
        headers: headers
    });
}
