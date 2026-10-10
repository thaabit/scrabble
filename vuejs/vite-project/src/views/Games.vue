<template>
<div class="title">Active Games</div>
<div v-for="(game) in games.active.value"
    @click="turns.change(game.id)"
    class="game clickable"
>
    <div :class="[game.my_turn ? 'current' : '']">
        <img v-if="profile.avatar" :src="profile.avatar.value" style="width:50px;">
        <img v-else :src="default_avatar" style="width:50px;background:#000;">
        {{ curUsername }} {{ game.scores[curUsername] }}
    </div>
    <div :class="[!game.my_turn ? 'current' : '']">
        <img v-if="game.avatar" :src="game.avatar" style="width:50px;">
        <img v-else :src="default_avatar" style="width:50px;background:#000;">
        {{ game.opponent }} {{ game.scores[game.opponent] }}
    </div>
    <div class="center"><button @click="turns.change(game.id)">Go</button></div>
</div>

<!--unacknowledged finished games-->
<div class="title" v-if="games.finished.value.length && games.finished.value.length > 0">Finished Games</div>
<div v-for="(game) in games.finished.value"
     @click="turns.change(game.id)"
     class="game clickable"
>
    <div :class="[game.winner===curUsername ? 'winner' : '']">
        <img v-if="profile.avatar" :src="profile.avatar.value" style="width:50px;">
        <img v-else :src="default_avatar" style="width:50px;background:#000;">
        {{curUsername}} {{ game.scores[curUsername] }}
    </div>
    <div :class="[game.winner===game.opponent ? 'winner' : '']">
        <img v-if="game.avatar" :src="game.avatar" style="width:50px;">
        <img v-else :src="default_avatar" style="width:50px;background:#000;">
        {{ game.opponent }} {{ game.scores[game.opponent] }}
    </div>
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
const profile = inject('profile')

function acknowledge_game(game_id) {
    http.patch('/game/acknowledge/' + game_id).then(response => {
        games.refresh()
    })
}

const turns = inject('turns')
const default_avatar = inject('default_avatar')
onMounted(() => {
    games.refresh()
    turns.refresh()
})

</script>

