import { defineStore } from 'pinia';
import { router } from '@/helpers/router.js';

export const useAuthStore = defineStore('auth', {
    id: 'auth',
    state: () => ({
        token: localStorage.getItem('jwt'),
    }),
    actions: {
        store(token) {
            if (token) localStorage.setItem('jwt', token);
        },

        logout() {
            this.token = null;
            localStorage.removeItem('jwt');
            router.push('/login');
        },
        parseJWT() {
            if (this.token) {
                let payload = (this.token.split('.')[1])
                return JSON.parse(atob(payload))
            }
            return {}
        },
        isLoggedIn() {
            return (this.token)

        },
    }
});
