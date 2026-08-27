<template>
<div id="top">
    <template v-if="isAuthenticated">
    <RouterLink to="/games">Games  <span v-if="turnCount">({{turnCount}})</span></RouterLink> |
    <RouterLink to="/archive">Archive</RouterLink> |
    <RouterLink to="/friends">Friends </RouterLink> |
    <a @click="authStore.logout">Logout</a>
    </template>

    <template v-else>
    <RouterLink to="/signup">Signup | </RouterLink>
    <RouterLink to="/login">Login</RouterLink>
    </template>
</div>
<RouterView />
</template>
<script setup>
    import { router } from '@/helpers/router.js'
    import { storeToRefs } from 'pinia'
    import { useAuthStore } from '@/stores/auth.store.js'
    import { ref, provide } from 'vue'

    const authStore = useAuthStore();
    const { isAuthenticated, loggedInUser } = storeToRefs(authStore)
    const turnCount = ref(0)
    provide('turnCount', turnCount)
</script>
