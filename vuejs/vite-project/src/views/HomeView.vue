<template>
    <!-- active games -->
    <div class="all-games">
    <div class="title">Active Games</div>
    <div v-for="(game) in games"
        @click="changeGame(game.id)"
        class="game clickable"
    >
    <div :class="(game.my_turn) ? 'current' : ''">
        <div class="user">You {{ game.scores[authUsername] }}</div>
    </div>
    <div :class="(!game.my_turn) ? 'current' : ''">
        <div class="user">{{ game.opponent }} {{ game.scores[game.opponent] }}</div>
    </div>
    </div>
    </div>
</template>
<script setup>
    import { ref, onMounted } from 'vue'
    import { http } from '@/helpers/api.js';
    import { router } from '@/helpers/router.js'
    import { useRoute } from 'vue-router';
    import { useAuthStore } from '@/stores/auth.store.js'

    const route = useRoute()
    const games = ref([])
    const turnCount = ref(null)
    const authUsername = useAuthStore().parseJWT().sub

    function changeGame(id) {
        if (id != route?.params?.id) {
            router.push(`/game/${id}`)
            closegamesDialog()
        }
    }
    onMounted(() => {
        http.get('/game?type=active').then(response => {
            games.value = response.data.filter(game => {
                return Number(game.id) !== Number(route.params.id)
            })
            turnCount.value = response.data.filter(game => {
                return game.whose_turn === authUsername
            }).length
            document.title = turnCount.value > 0 ? `(${turnCount}) - Games` : 'Games'
        })
        .catch(error => {
        console.log(error)
            const msg = (error.data && error.data.detail) || error.statusText;
            throw new Error(msg);
        });
    })
</script>
