<script setup>
import { http } from '@/helpers/api.js';
import { ref, onMounted } from 'vue'
const games = ref()

onMounted(() => {
    http.get('/games').then(response => {
        console.log(response.data)
        games.value = response.data
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    });
})

</script>

<template>
  <h1>Games</h1>
  <div v-for="(game) in games"><RouterLink :to="{ name: 'game', params: { id: game.id } }">{{game.id}}</RouterLink></div>
</template>

