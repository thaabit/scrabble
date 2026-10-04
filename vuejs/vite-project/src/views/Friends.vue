<template>
<h1>Friends</h1>
<div class="friends" v-for="(user) in users">
    <div class="user">{{user}}</div>
    <div><button @click="newGame(user)">New Game</button></div>
</div>
</template>

<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted, inject } from 'vue'
import { router } from '@/helpers/router.js';
const users = ref()

onMounted(() => {
    http.get('/user').then(response => {
        users.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    })
})
const turns = inject('turns')
function newGame(other_user) {
    http.post('/game', { opponent: other_user }).then(response => {
        turns.refresh()
        router.push(`/game/${response.data.id}`)
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });
}
</script>


