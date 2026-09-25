<template>
<div id="top">
    <template v-if="isAuthenticated">
    <span>
    <RouterLink to="/games">Games <span v-if="turnCount">({{turnCount}})</span></RouterLink>
    | <RouterLink to="/archive">Archive</RouterLink>
    | <RouterLink to="/friends">New Game</RouterLink>
    </span>
    <span class="dropdown">
        <img v-if="isAuthenticated" :src="curUserAvatar" alt="avatar" style="width:50px;">
        <div class="dropdown-content">
            <span v-if="isAuthenticated">
                <RouterLink to="/profile">Profile </RouterLink><br>
                <a @click="authStore.logout">Logout</a><br>
            </span>
            <span v-else>

            </span>
        </div>
    </span>

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
    import { ref, provide, onMounted, onUnmounted } from 'vue'
    import { http } from '@/helpers/api.js';

    const authStore = useAuthStore();
    const { isAuthenticated } = storeToRefs(authStore)
    const turnCount = ref(0)
    const curUser = ref({})
    const curUserAvatar = ref('')

    provide('turnCount', turnCount)
    provide('curUser', curUser)
    provide('curUserAvatar', curUser.value.avatar)

    function refreshProfile() {
        http.get('/profile').then(response => {
            if (response.data.avatar) response.data.avatar = '/' + response.data.avatar + "?t=" + Date.now()
            else response.data.avatar = '/public/default_avatar.png'
            curUserAvatar.value = response.data.avatar
            curUser.value = response.data
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        })
    }
    refreshProfile()
    function refreshTurnCount() {
        http.get('/turn').then(response => {
            turnCount.value = response.data.turns
            document.title = "Scrabble (" + turnCount.value + ")"
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    }
    refreshTurnCount()
    let interval
    onMounted(() => {
        interval = setInterval(refreshTurnCount, 1000*30)
    })
    onUnmounted(() => {
        clearInterval(interval);
    })
</script>
