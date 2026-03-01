<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const menuList = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/resource/menu')
    menuList.value = res.data
  } catch (err) {
    console.error('Failed to fetch menu', err)
  }
})

const go = (path) => {
  router.push(path)
}
</script>

<template>
  <aside class="sidebar">
    <h2 class="logo">Admin</h2>
    <ul>
      <li v-for="item in menuList" :key="item.id">
        <a @click.prevent="go(item.path)">{{ item.title }}</a>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  background: #1e293b;
  color: white;
  padding: 20px;
}
.sidebar ul {
  list-style: none;
  padding: 0;
}
.sidebar li {
  margin: 15px 0;
}
.sidebar a {
  color: white;
  text-decoration: none;
  cursor: pointer;
}
.sidebar a.router-link-active {
  font-weight: bold;
  color: #38bdf8;
}
</style>
