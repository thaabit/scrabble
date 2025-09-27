<script setup>
import { http } from '@/helpers/api.js';
import { Form, Field } from 'vee-validate';
import * as Yup from 'yup';
import { useAuthStore } from '@/stores/auth.store.js';
import { router } from '@/helpers/router.js';

const schema = Yup.object().shape({
    username: Yup.string().required('Username is required'),
    password: Yup.string().required('Password is required')
});

function login(values) {
    const { username, password } = values
    const { token, logout, store } = useAuthStore();
    http.post('/login', {
        username: username,
        password: password,
    }).then(response => {
        store(response.data.access_token)
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        console.error('Error creating item:', msg);
        if ([401, 403].includes(error.status) && token) logout();
        throw new Error(msg);
    });
}
</script>

<template>
  <h1>Login</h1>
  <p class="error" v-if="error">{{ error }}</p>
  <Form @submit="login" :validation-schema="schema">
    <Field name="username" placeholder="Username" data-1p-ignore />
    <Field name="password" type="password" placeholder="Password" data-1p-ignore />
  <button>Login</button>
  </Form>
</template>

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
