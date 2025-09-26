import { createApp } from 'vue'
import { createPinia, defineStore } from 'pinia'
import './style.css'

import App from './App.vue'
import { router } from './helpers/router.js';

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
