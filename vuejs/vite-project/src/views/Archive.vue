<template>
    <br>
    <table class="archive">
        <tr>
            <th>Me</th>
            <th>Them</th>
            <th>Opponent</th>
            <th>Started</th>
            <th>Finished</th>
        </tr>
        <tr v-for="(game) in games"
            @click="changeGame(game.id)"
            class="clickable"
        >
            <td :class="[game.winner===curUser.username  ? 'winner' : '']">{{game.scores[curUser.username]}}</td>
            <td :class="[game.winner===game.opponent ? 'winner' : '']">{{game.scores[game.opponent]}}</td>
            <td>{{ game.opponent }}</td>
            <td>{{ useDateFormat(game.started, 'MMM Do, YYYY')}}</td>
            <td>{{ useDateFormat(game.finished_date, 'MMM Do, YYYY')}}</td>
        </tr>
    </table>
</template>
<script setup>
import { useDateFormat } from '@vueuse/core';
import { http } from '@/helpers/api.js';
import { ref, onMounted, inject } from 'vue'
import { useAuthStore } from '@/stores/auth.store.js'
import { router } from '@/helpers/router.js'
const games = ref([])
const curUser = inject('curUser')

function changeGame(id) {
    router.push(`/game/${id}`)
}

onMounted(() => {
    http.get('/game?type=inactive').then(response => {
        games.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });

})

</script>

