<template>
<div id="top">
    <template v-if="isAuthenticated">
    <span>
    <RouterLink to="/games" @click.native.prevent="refreshAll">Games <span v-if="turnCount">({{turnCount}})</span></RouterLink>
    | <RouterLink to="/archive">Archive</RouterLink>
    | <RouterLink to="/friends">New Game</RouterLink>
    </span>
    <span class="dropdown">
        <img v-if="isAuthenticated" :src="curAvatar" alt="avatar" style="width:50px;">
        <div class="dropdown-content">
            <span v-if="isAuthenticated">
                <RouterLink to="/profile">Profile </RouterLink><br>
                <a @click="authStore.logout">Logout</a><br>
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
    import { ref, provide, inject, onMounted, onUnmounted } from 'vue'
    import { http } from '@/helpers/api.js';

    const authStore = useAuthStore();
    const { isAuthenticated } = storeToRefs(authStore)

    const turnCount = ref(0)
    provide('turns', {
        count: turnCount,
        refresh: refreshTurnCount,
    })

    const curUsername = ref('')
    const curName = ref('')
    const curAvatar = ref('')
    provide('profile', {
        avatar: curAvatar,
        username: curUsername,
        name: curName,
    })

    const activeGames = ref([])
    const finishedGames = ref([])
    provide('games', {
        active: activeGames,
        finished: finishedGames,
        refresh: refreshGameList,
    });

    function refreshGameList() {
        http.get('/game?type=active').then(response => {
            activeGames.value = response.data
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText
            throw new Error(msg)
        });
        http.get('/game?type=unacknowledged').then(response => {
            finishedGames.value = response.data
        })
        .catch(error => {
            console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText
            throw new Error(msg)
        });
    }

    function refreshProfile() {
        http.get('/profile').then(response => {
            if (response.data.avatar) response.data.avatar = '/' + response.data.avatar + "?t=" + Date.now()
            else response.data.avatar = '/public/default_avatar.png'
            curAvatar.value = response.data.avatar
            curUsername.value = response.data.username
            curName.value = response.data.name
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        })
    }

    function refreshAll() {
        refreshTurnCount()
        refreshGameList()
    }
    function refreshTurnCount() {
        http.get('/turn').then(response => {
            turnCount.value = response.data.turns
            let t = "Scrabble"
            if (turnCount.value > 0) t = "(" + turnCount.value + ") " + t
            document.title = t
        })
        .catch(error => {
            const msg = (error.data && error.data.detail) || error.statusText
            console.log(error)
            throw new Error(msg)
        });
    }

    refreshProfile()
    refreshTurnCount()
    let interval
    onMounted(() => {
        interval = setInterval(refreshTurnCount, 1000*30)
    })
    onUnmounted(() => {
        clearInterval(interval);
    })
</script>
