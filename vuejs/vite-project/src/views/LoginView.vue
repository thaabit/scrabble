<template>
  <h1>Login</h1>
  <p v-if="apiError" class="error">{{ apiError }}</p>
  <Form @submit="login" :validation-schema="schema">
    <Field name="username" placeholder="Username" data-1p-ignore />
    <Field name="password" type="password" placeholder="Password" data-1p-ignore />
  <button>Login</button>
  </Form>
</template>

<script setup>
import { ref } from 'vue'
import { http } from '@/helpers/api.js';
import { Form, Field } from 'vee-validate';
import * as Yup from 'yup';
import { useAuthStore } from '@/stores/auth.store.js';
import { router } from '@/helpers/router.js';

const schema = Yup.object().shape({
    username: Yup.string().required('Username is required'),
    password: Yup.string().required('Password is required')
});

const apiError = ref(null)

function login(values) {
    const { username, password } = values
    const { store } = useAuthStore();
    http.post('/login', {
        username: username,
        password: password,
    }).then(response => {
        store(response.data.access_token)
        console.log("logged in")
        router.push('/');
    })
    .catch(error => {
        const msg = error.response?.data?.detail || error.detail || error.statusText;
        console.error('Error logging in:', error);
        apiError.value = msg 
    });
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
