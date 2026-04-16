<template>
  <div class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/">StudyStride</router-link>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="navbar-item">首页</router-link>
        <router-link to="/history" class="navbar-item">历史记录</router-link>
        <router-link to="/settings" class="navbar-item">设置</router-link>
        <router-link v-if="!auth.isLoggedIn" to="/login" class="navbar-item">登录</router-link>
        <span v-else class="navbar-user">
          <span class="navbar-email">{{ auth.user?.email }}</span>
          <button type="button" class="logout-btn" @click="logout">退出</button>
        </span>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer">
      <p>&copy; {{ new Date().getFullYear() }} StudyStride - 学习打卡应用</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()

const logout = async () => {
  await auth.signOut()
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
  color: #333;
  line-height: 1.6;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background-color: #333;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.navbar-menu {
  display: flex;
  gap: 1.5rem;
}

.navbar-item {
  color: white;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s;
}

.navbar-item:hover {
  color: #4CAF50;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #fff;
  font-size: 0.9rem;
}

.navbar-email {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.6);
  color: #fff;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.logout-btn:hover {
  border-color: #4caf50;
  color: #4caf50;
}

.main-content {
  flex: 1;
  padding: 2rem;
}

.footer {
  background-color: #333;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .navbar-menu {
    width: 100%;
    justify-content: center;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>
