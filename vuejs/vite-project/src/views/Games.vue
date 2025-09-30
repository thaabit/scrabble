<template>
    <div>Archived Games</div>
    <table>
        <tr>
            <th>Opponent</th>
            <th>Started</th>
            <th>Finished</th>
            <th>Score</th>
        </tr>
        <tr v-for="(game) in games"
            @click="changeGame(game.id)"
            class="clickable"
        >
            <td>{{game.opponent}}</td>
            <td>{{game.started}}</td>
            <td>{{game.finished_date}}</td>
            <td>{{game.scores[auth_username]}} - {{game.scores[game.opponent]}}</td>
        </tr>
    </table>
</template>
<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store.js'
import { router } from '@/helpers/router.js'
const games = ref([])
const auth_username = useAuthStore().parseJWT().sub

function changeGame(id) {
    router.push(`/game/${id}`)
}

onMounted(() => {
    http.get('/game?type=inactive').then(response => {
        console.log(response.data)
        games.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });

})

</script>

