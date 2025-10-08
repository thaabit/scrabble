<template>
<div id="top">
    <template v-if="isAuthenticated">
    <RouterLink to="/">Home | </RouterLink>
    <RouterLink to="/games">Archive | </RouterLink>
    <RouterLink to="/friends">Friends | </RouterLink>
    <a @click="authStore.logout">Logout</a>
    {{ authStore.parseJWT().sub }}
    <button @click="showNewGameDialog">New Game</button>
    </template>

    <template v-else>
    <RouterLink to="/signup">Signup | </RouterLink>
    <RouterLink to="/login">Login</RouterLink>
    </template>
</div>
<RouterView />
<Dialog ref="newGameDialog">
  <div v-for="(user) in users">{{user}} <button @click="newGame(user)">New Game</button></div>
</Dialog>
</template>
<script setup>
    import { ref, computed, useTemplateRef, onMounted } from 'vue';
    import { useAuthStore } from '@/stores/auth.store.js';
    import { storeToRefs } from 'pinia'
    import { http } from '@/helpers/api.js';
    import { router } from '@/helpers/router.js'
    import Dialog from '@/components/Dialog.vue'

    const authStore = useAuthStore();
    const { isAuthenticated, loggedInUser } = storeToRefs(authStore)

    const newGameDialog = useTemplateRef('newGameDialog')
    const showNewGameDialog = () => newGameDialog.value.show()
    const users = ref([])
    onMounted(() => {
        http.get('/user').then(response => {
            users.value = response.data
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        })
    })
    function newGame(other_user) {
        http.post('/game', { opponent: other_user }).then(response => {
            newGameDialog.value.close()
            router.push(`/game/${response.data.id}`)
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    }
</script>
