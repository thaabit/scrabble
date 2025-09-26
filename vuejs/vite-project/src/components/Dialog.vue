<script setup>
import { ref } from 'vue'

const dialogRef = ref(null)
const show  = () => dialogRef.value?.showModal()
const close = () => dialogRef.value?.close()

function closeOnClick(e) {
    if (e.currentTarget === e.target) close()
}

defineExpose({
    show, close,
})
</script>

<template>
    <dialog ref="dialogRef" @click="closeOnClick" class="">
        <slot />
    </dialog>
</template>
