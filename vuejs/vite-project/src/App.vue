<script setup>
    import { useAuthStore } from '@/stores/auth.store.js';
    const { logout, isLoggedIn } = useAuthStore();

</script>
<template>
<div id="top">
    <RouterLink to="/">Home</RouterLink> |
    <RouterLink v-if="!isLoggedIn" to="/signup">Signup !</RouterLink>
    <RouterLink v-if="!isLoggedIn" to="/login">Login !</RouterLink>
    <RouterLink to="/games">Games </RouterLink> |
    <RouterLink to="/friends">Friends</RouterLink> |
    <a v-if="isLoggedIn" @click="logout">Logout</a>
</div>
<RouterView />
</template>
