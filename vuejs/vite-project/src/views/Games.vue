<template>
<div class="title">Active Games</div>
<div v-for="(game) in active_games"
    @click="changeGame(game.id)"
    class="game clickable"
>
    <div :class="[game.my_turn ? 'current' : '']">
        {{ curUsername }} {{ game.scores[curUsername] }}
    </div>
    <div :class="[!game.my_turn ? 'current' : '']">
        {{ game.opponent }} {{ game.scores[game.opponent] }}
    </div>
    <div class="center"><button @click="changeGame(game.id)">Go</button></div>
</div>

<!--unacknowledged finished games-->
<div class="title" v-if="finished_games.length > 0">Finished Games</div>
<div v-for="(game) in finished_games"
     @click="changeGame(game.id)"
     class="game clickable"
>
    <div :class="[game.winner===curUsername ? 'winner' : '']">{{curUsername}} {{ game.scores[curUsername] }}</div>
    <div :class="[game.winner===game.opponent ? 'winner' : '']">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
    <div><button @click.stop="acknowledge_game(game.id)">Dismiss</button></div>
</div>
</template>

<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted, inject } from 'vue'
import { useAuthStore } from '@/stores/auth.store.js'
import { router } from '@/helpers/router.js'
const curUsername = useAuthStore().authedUser

const active_games = ref([])
const finished_games = ref([])

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

