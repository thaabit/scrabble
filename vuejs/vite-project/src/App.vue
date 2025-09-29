<script setup>
    import { useAuthStore } from '@/stores/auth.store.js';
    import { ref, computed } from 'vue';
    import { storeToRefs } from 'pinia'
    const authStore = useAuthStore();
    const { isAuthenticated } = storeToRefs(authStore)
    console.log(isAuthenticated.value)
</script>
<template>
<div id="top">
    <template v-if="isAuthenticated">
    <RouterLink to="/">Home | </RouterLink>
    <RouterLink to="/games">Games | </RouterLink>
    <RouterLink to="/friends">Friends | </RouterLink>
    <a @click="authStore.logout">Logout</a>
    </template>

    <template v-else>
    <RouterLink to="/signup">Signup | </RouterLink>
    <RouterLink to="/login">Login</RouterLink>
    </template>
</div>
<RouterView />
</template>
