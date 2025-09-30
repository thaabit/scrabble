<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted } from 'vue'
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

function newGame(other_user) {
    http.post('/game', { opponent: other_user }).then(response => {
        console.log(response)
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });
}
</script>

<template>
  <h1>Friends</h1>
  <div v-for="(user) in users">{{user}} <button @click="newGame(user)">New Game</button></div>
</template>

