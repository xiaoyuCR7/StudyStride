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
        <button type="button" class="theme-toggle" @click="toggleTheme">
          <span v-if="isLightTheme">🌙</span>
          <span v-else>☀️</span>
        </button>
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import logo from './assets/logo.png'

const auth = useAuthStore()
const isLightTheme = ref(false)

// 主题切换函数
const toggleTheme = () => {
  isLightTheme.value = !isLightTheme.value
  if (isLightTheme.value) {
    document.documentElement.classList.add('light')
    localStorage.setItem('theme', 'light')
  } else {
    document.documentElement.classList.remove('light')
    localStorage.setItem('theme', 'dark')
  }
}

// 初始化主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  isLightTheme.value = savedTheme === 'light'
  if (isLightTheme.value) {
    document.documentElement.classList.add('light')
  }
})

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
  background: var(--background-gradient);
  color: var(--text-color);
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
  background: var(--navbar-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--navbar-border);
  color: var(--text-color);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--navbar-shadow);
  transition: all 0.3s ease;
}

.navbar:hover {
  box-shadow: var(--navbar-hover-shadow);
}

.navbar-brand .brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-color);
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
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-menu {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.navbar-item {
  color: var(--text-color);
  text-decoration: none;
  font-size: 1rem;
  transition: all 0.3s ease;
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.navbar-item:hover {
  color: var(--text-color);
  background: var(--navbar-item-bg);
  transform: translateY(-2px);
  box-shadow: var(--navbar-item-shadow);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-color);
  font-size: 0.9rem;
  background: var(--navbar-user-bg);
  padding: 0.5rem 1rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--navbar-user-border);
}

.navbar-email {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  background: var(--logout-btn-bg);
  border: 1px solid var(--logout-btn-border);
  color: var(--text-color);
  padding: 0.25rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: var(--logout-btn-shadow);
}

.logout-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px 0 rgba(156, 39, 176, 0.3);
}

.theme-toggle {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-color);
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  box-shadow: var(--glass-shadow);
}

.theme-toggle:hover {
  border-color: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: var(--button-hover-shadow);
}

.theme-toggle:active {
  transform: translateY(1px);
  box-shadow: var(--button-active-shadow);
}

.main-content {
  flex: 1;
  padding: 2rem;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.footer {
  background: var(--footer-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid var(--footer-border);
  color: var(--text-color);
  text-align: center;
  padding: 1rem;
  margin-top: 2rem;
  box-shadow: var(--footer-shadow);
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
  
  .theme-toggle {
    order: -1;
    margin-bottom: 0.5rem;
  }
}
</style>
