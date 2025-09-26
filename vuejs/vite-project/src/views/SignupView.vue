<template>
  <h1>Signup</h1>
  <p class="error" v-if="error">{{ error }}</p>
  <form>
  <input type="text" placeholder="Username" v-model="username" data-1p-ignore />
  <input type="password" placeholder="Password" v-model="password" data-1p-ignore />
  <button @click.prevent="signup">Sign up</button>
  </form>
</template>
<script>
import { axiosWrapper } from '@/helpers/axios-wrapper.js';
export default {
    name: 'Signup',
    data() {
        return {
            username: '',
            password: '',
            error: '',
        }
    },
    methods: {
        signup() {
            this.error = ''
            let data = axiosWrapper.post("user", {
                username: this.username,
                password: this.password
            })
            if (data.error) this.error = data.error
        }
    }
}
</script>
<style>
.error { color: red }
form {
    margin:auto;
    max-width: 400px;
    border: 2px solid #555;
    border-radius: 8px;
    padding: 20px;
    background:#ddd;
}

input {
    transition: border-color 0.3s ease;
    border: 1px solid #ccc;
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
    width:350px;
    background:white;
    color:#555;
    font-size:larger;
}
input::placeholder {
    color: #ccc
}

input:focus {
    border: 2px solid #ccc;
    outline: none;
}

</style>
