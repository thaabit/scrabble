<template>
<div class="title">Active Games</div>
<div v-for="(game) in games.active.value"
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
<div class="title" v-if="games.finished.value.length && games.finished.value.length > 0">Finished Games</div>
<div v-for="(game) in games.finished.value"
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
const games = inject('games')

function acknowledge_game(game_id) {
    http.patch('/game/acknowledge/' + game_id).then(response => {
        games.refresh()
    })
}

function changeGame(id) {
    router.push(`/game/${id}`)
}

const turns = inject('turns')
onMounted(() => {
    games.refresh()
    turns.refresh()
})

</script>

