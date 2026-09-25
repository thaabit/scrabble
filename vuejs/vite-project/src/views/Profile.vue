<template>
  <h1>Profile</h1>
  <p v-if="apiError" class="error">{{ apiError }}</p>
  <Form @submit="updateProfile" :validation-schema="schema">
    <label for="avatar" class="btn clickable ctr dropdown">
        <span v-if="avatar">
            <img :src="avatar" alt="avatar" >
            <div class="dropdown-content">
                <button class="ctr" v-if="avatar" @click="deleteAvatar">Remove Avatar</button>
            </div>
        </span>
        <span v-else>
            <img src="/public/default_avatar.png" style="width:100px;background-color: transparent;">
        </span>
    </label>
    <input
      id="avatar"
      class="ctr"
      type="file"
      @change="uploadAvatar"
      accept="image/*"
      capture
      hidden
    />
    <br>
    <label for="name">Name</label>
    <Field name="name" id="name" v-model="name" type="text" placeholder="Name" data-1p-ignore />
    <ErrorMessage name="name" />

    <label for="password">Username</label>
    <Field name="username" id="name" v-model="username" type="text" placeholder="Username" data-1p-ignore />
    <ErrorMessage name="username" />

    <label for="password">Password</label>
    <Field name="password" id="name" type="password" placeholder="Password" data-1p-ignore />
    <ErrorMessage name="password" />

  <button>Update Profile</button>
  </Form>
</template>

<script setup>

import { ref, onMounted, inject } from 'vue'
import { http } from '@/helpers/api.js';
import { Form, Field, ErrorMessage } from 'vee-validate';
import * as Yup from 'yup';
import { useAuthStore } from '@/stores/auth.store.js';
import { router } from '@/helpers/router.js';
const avatar = ref(null)
const name = ref('')
const username = ref('')
const schema = Yup.object().shape({
    username: Yup.string().required().min(5),
    name: Yup.string().required()
});


onMounted(() => {
    refreshProfile()
})

function refreshProfile() {
    http.get('/profile').then(response => {
        avatar.value = response.data.avatar
        username.value = response.data.username
        name.value = response.data.name
        if (avatar.value) avatar.value = '/' + response.data.avatar + "?t=" + Date.now()
    })
    .catch(error => {
        warn(error)
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    })
}
function deleteAvatar() {
    http.delete('/profile/avatar').then(response => {
        refreshProfile()
    })
    .catch(error => {
        warn(error)
        const msg = (error.data && error.data.detail) || error.statusText;
        throw new Error(msg);
    })
}

const apiError = ref(null)
const file = ref(null)

const uploadAvatar = (event) => {
    console.log(event.target.files[0])
    file.value = event.target.files[0]
    if (!file.value) return

    http.patch('/profile/avatar', {
        file: file.value,
    }, { 'Content-Type': 'multipart/form-data' }).then(response => {
        console.log(response)
        refreshProfile()
    })
    .catch(error => {
        const msg = error.response?.data?.detail || error.detail || error.statusText;
        console.error('Error logging in:', error);
        apiError.value = msg 
    });
}

function updateProfile(values) {
    const { name, username, password } = values
    const { store } = useAuthStore();
    const data = {
        username: username,
        name: name,
    }
    if (password) data.password = password
    console.log(data)
    http.patch('/profile', data).then(response => {
        console.log(response)
        refreshProfile()
    })
    .catch(error => {
        const msg = error.response?.data?.detail || error.detail || error.statusText;
        console.error('Error updating profile:', error);
        apiError.value = msg 
    });
}
</script>



