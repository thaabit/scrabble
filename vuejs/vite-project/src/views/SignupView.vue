<script setup>
import { http } from '@/helpers/api.js';
import { Form, Field } from 'vee-validate'
import * as Yup from 'yup'
import { router } from '@/helpers/router.js';

const schema = Yup.object().shape({
    username: Yup.string().required('Username is required'),
    password: Yup.string().required('Password is required')
});
function signup(values) {
    const { username, password } = values
    let body = {
        username: username,
        password: password,
    }
    http.post('/user', body).then(response => {
        const { store } = useAuthStore();
        console.log(response.data)
        store(response.data.access_token)
        //router.push('/friends')
    })
    .catch(error => {
        const msg = (error.data && error.data.detail) || error.statusText;
        console.error('Error creating item:', msg);
        throw new Error(msg);
    });
}
</script>

<template>
  <h1>Signup</h1>
  <Form @submit="signup" :validation-schema="schema">
  <Field name="username" placeholder="Username" data-1p-ignore />
  <Field name="password" type="password" placeholder="Password" data-1p-ignore />
  <button>Signup</button>
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
