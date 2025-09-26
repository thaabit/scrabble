<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted } from 'vue'
const users = ref()

onMounted(() => {
    console.log("blah")
    http.get('/users').then(response => {
    console.log("then")
        console.log(response)
        users.value = response.data
    })
    .catch(error => {
        console.log("error")
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    })
    .finally(
        console.log("finally")

    );
    console.log("done")
})

function newGame(other_user) {
    console.log(other_user)
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

