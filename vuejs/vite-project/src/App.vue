<script setup>
    import { useAuthStore } from '@/stores/auth.store.js';
    const { logout } = useAuthStore();

</script>
<template>
    <RouterLink to="/">Home</RouterLink> |
    <RouterLink to="/signup">Signup</RouterLink> |
    <RouterLink to="/login">Login</RouterLink> |
    <RouterLink to="/games">Games</RouterLink> |
    <RouterLink to="/friends">Friends</RouterLink> |
    <button @click="logout">Logout</button>
    <RouterView />
</template>
