import { useRoute, createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store.js';
import { computed } from 'vue'

import LoginView    from '@/views/Login.vue'
import SignupView   from '@/views/Signup.vue'
import MainView     from '@/views/Main.vue'
import ArchiveView  from '@/views/Archive.vue'
import FriendsView  from '@/views/Friends.vue'
import GamesView    from '@/views/Games.vue'

import { useFavicon } from '@vueuse/core'
const favicon = useFavicon()
favicon.value = import.meta.env.MODE === 'development' ? '/favicon-dev.ico' : 'favicon-prod.ico'

export const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    linkActiveClass: 'active',
    routes: [
        { path: '/',        component: MainView },
        { path: '/login',   component: LoginView },
        { path: '/signup',  component: SignupView },
        { path: '/archive', component: ArchiveView },
        { path: '/friends', component: FriendsView },
        { path: '/games',   component: GamesView },
        { name: 'game', path: '/game/:id(\\d+)', component: MainView },
    ]
});

router.beforeEach(to => {
    // redirect to login page if not logged in and trying to access a restricted page
    const publicPages = ['/login','/','/signup'];
    const authRequired = !publicPages.includes(to.path);
    const auth = useAuthStore();
    if (authRequired && !auth.token) {
        auth.returnUrl = to.fullPath;
        return '/login';
    }
});

const DEFAULT_TITLE = import.meta.env.MODE;
