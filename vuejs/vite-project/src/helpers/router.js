import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store.js';

import HomeView     from '@/views/HomeView.vue'
import LoginView    from '@/views/LoginView.vue'
import SignupView   from '@/views/SignupView.vue'
import GameView     from '@/views/GameView.vue'
import Games        from '@/views/Games.vue'
import Friends      from '@/views/Friends.vue'

export const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    linkActiveClass: 'active',
    routes: [
        { path: '/', component: GameView },
        { path: '/login', component: LoginView },
        { path: '/signup', component: SignupView },
        { name: 'game', path: '/game/:id(\\d+)', component: GameView },
        { path: '/games', component: Games },
        { path: '/friends', component: Friends },
    ]
});

router.beforeEach(async (to) => {
    // redirect to login page if not logged in and trying to access a restricted page
    const publicPages = ['/login','/'];
    const authRequired = !publicPages.includes(to.path);
    const auth = useAuthStore();
    console.log(auth.parseJWT().sub)
    if (authRequired && !auth.token) {
        auth.returnUrl = to.fullPath;
        return '/login';
    }
});
