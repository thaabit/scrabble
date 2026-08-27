<template>
<div class="title">Active Games</div>
<div class="other-games">
    <div v-for="(game) in active_games"
        @click="changeGame(game.id)"
        class="game clickable"
    >
        <div :class="['user', game.my_turn ? 'current' : '']">
            {{ authUsername }} {{ game.scores[authUsername] }}
        </div>
        <div :class="['user', !game.my_turn ? 'current' : '']">
            {{ game.opponent }} {{ game.scores[game.opponent] }}
        </div>
        <div class="center"><button @click="changeGame(game.id)">Go</button></div>
    </div>
</div>

<!--unacknowledged finished games-->
<div class="title" v-if="finished_games.length > 0">Finished Games</div>
<div v-for="(game) in finished_games"
     @click="changeGame(game.id)"
     class="other-games game clickable"
>
    <div class="user">You {{ game.scores[authUsername] }}</div>
    <div class="user">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
    <div><button @click.prevent="acknowledge_game(game.id)">Dismiss</button></div>
</div>
</template>

<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store.js'
import { router } from '@/helpers/router.js'

const active_games = ref([])
const finished_games = ref([])
const authUsername = useAuthStore().parseJWT().sub

function acknowledge_game(game_id) {
    http.patch('/game/acknowledge/' + game_id).then(response => {
        refreshGameList()
    })
}

function changeGame(id) {
    router.push(`/game/${id}`)
}

function refreshGameList() {
    http.get('/game?type=active').then(response => {
        active_games.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });
    http.get('/game?type=unacknowledged').then(response => {
        finished_games.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });
}

onMounted(() => {
    refreshGameList();
})

</script>

