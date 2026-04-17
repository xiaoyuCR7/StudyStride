<template>
  <div class="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <img :src="logo" alt="StudyStride" class="brand-logo" />
          <span class="brand-name">StudyStride</span>
        </router-link>
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
import logo from './assets/logo.png'

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
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: rgba(255, 255, 255, 0.87);
  line-height: 1.6;
  min-height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.navbar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  transition: all 0.3s ease;
}

.navbar:hover {
  box-shadow: 0 12px 40px 0 rgba(156, 39, 176, 0.4);
}

.navbar-brand .brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
}

.navbar-brand .brand-link:hover {
  transform: scale(1.05);
}

.navbar-brand .brand-logo {
  height: 32px;
  width: 32px;
  object-fit: contain;
}

.navbar-brand .brand-name {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-menu {
  display: flex;
  gap: 1.5rem;
}

.navbar-item {
  color: rgba(255, 255, 255, 0.87);
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s ease;
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.navbar-item:hover {
  color: #ffffff;
  background: rgba(156, 39, 176, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.87);
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.navbar-email {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.87);
  padding: 0.25rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  border-color: #d500f9;
  color: #d500f9;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.logout-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px 0 rgba(156, 39, 176, 0.3);
}

.main-content {
  flex: 1;
  padding: 2rem;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.87);
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
  box-shadow: 0 -8px 32px 0 rgba(31, 38, 135, 0.37);
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
    flex-wrap: wrap;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .navbar-user {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>
