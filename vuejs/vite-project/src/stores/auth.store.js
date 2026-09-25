import { defineStore } from 'pinia';
import { router } from '@/helpers/router.js';

export const useAuthStore = defineStore('auth', {
    id: 'auth',
    state: () => ({
        token: localStorage.getItem('jwt'),
    }),
    getters: {
        isAuthenticated: (state) => !!state?.token,
        authedUser: (state) => {
            if (state.token) {
                let payload = (state.token.split('.')[1])
                return JSON.parse(atob(payload)).sub
            }
            return ''
        }
    },
    actions: {
        store(token) {
            if (token) {
                this.token = token;
                localStorage.setItem('jwt', token);
            }
        },

        logout() {
            this.token = null;
            localStorage.removeItem('jwt');
            router.push('/login');
        },
    }
});
