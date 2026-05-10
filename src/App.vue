<template>
  <div class="app" :class="{ 'hide-navbar': isHomePage }">
    <nav v-if="!isHomePage" class="navbar">
      <div class="navbar-brand">
        <router-link to="/study" class="brand-link">
          <img :src="logo" alt="StudyStride" class="brand-logo" />
          <span class="brand-name">StudyStride</span>
        </router-link>
      </div>
      <div class="navbar-menu">
        <router-link to="/study" class="navbar-item">首页</router-link>
        <router-link to="/history" class="navbar-item">历史记录</router-link>
        <router-link to="/community" class="navbar-item">学习社区</router-link>
        <router-link v-if="!auth.isLoggedIn" to="/settings" class="navbar-item">设置</router-link>
        <router-link v-if="!auth.isLoggedIn" to="/login" class="navbar-item">登录</router-link>
        <UserMenu v-else />
        <button type="button" class="theme-toggle" @click="toggleTheme">
          <span v-if="isLightTheme">🌙</span>
          <span v-else>☀️</span>
        </button>
      </div>
    </nav>
    <main class="main-content">
      <div v-if="!isHomePage" class="main-content__bg" aria-hidden="true">
        <video
          class="main-content__bg-video"
          autoplay
          muted
          loop
          playsinline
          :src="heroVideoSrc"
          @error="onHeroVideoError"
        />
        <div class="main-content__bg-noise" />
        <div class="main-content__bg-gradient" />
      </div>
      <div class="main-content__body">
        <router-view />
      </div>
    </main>
    <footer v-if="!isHomePage" class="footer">
      <p>&copy; {{ new Date().getFullYear() }} StudyStride - 学习打卡应用</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { HERO_VIDEO_CDN, heroVideoLocalUrl } from './lib/heroBackgroundVideo'
import logo from './assets/logo.png'
import UserMenu from './components/UserMenu.vue'

const route = useRoute()
const auth = useAuthStore()
const isLightTheme = ref(false)

const heroVideoSrc = ref(heroVideoLocalUrl())
let heroVideoFallbackTried = false

const onHeroVideoError = () => {
  if (!heroVideoFallbackTried && heroVideoSrc.value !== HERO_VIDEO_CDN) {
    heroVideoFallbackTried = true
    heroVideoSrc.value = HERO_VIDEO_CDN
  }
}

const isHomePage = computed(() => route.path === '/')

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


</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Almarai', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--background-gradient);
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
  min-height: 100vh;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  position: relative;
  z-index: 1;
}

.main-content__bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.main-content__bg-video {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  transform: translate(-50%, -50%) scale(1);
  min-width: 100%;
  min-height: 100%;
}

.main-content__bg-noise {
  position: absolute;
  inset: 0;
  opacity: 0.55;
  mix-blend-mode: overlay;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
}

.main-content__bg-gradient {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), transparent 42%, rgba(0, 0, 0, 0.6));
}

:root.light .main-content__bg-video {
  opacity: 0.28;
}

:root.light .main-content__bg-noise {
  opacity: 0.35;
}

:root.light .main-content__bg-gradient {
  background: linear-gradient(
    to bottom,
    rgba(244, 243, 235, 0.72),
    rgba(244, 243, 235, 0.55) 40%,
    rgba(244, 243, 235, 0.82)
  );
}

.navbar {
  position: relative;
  z-index: 10;
  background: var(--navbar-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--navbar-border);
  color: var(--text-color);
  padding: 0.75rem 1.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--navbar-shadow);
  transition: all 0.3s ease;
  border-radius: 0 0 1.25rem 1.25rem;
}

.navbar:hover {
  box-shadow: var(--navbar-hover-shadow);
}

.app.hide-navbar {
  min-height: 100vh;
}

.app.hide-navbar .main-content {
  padding: 0;
  max-width: 100%;
  margin: 0;
  min-height: 100vh;
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
  color: var(--nav-link);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  transition: all 0.25s ease;
  position: relative;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
}

.navbar-item:hover,
.navbar-item.router-link-active {
  color: var(--nav-link-hover);
  background: var(--navbar-item-bg);
  transform: translateY(-1px);
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
  font-family: inherit;
  box-shadow: var(--logout-btn-shadow);
  z-index: 10;
  position: relative;
}

.logout-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: var(--button-hover-shadow);
}

.logout-btn:active {
  transform: translateY(1px);
  box-shadow: var(--button-active-shadow);
}

.logout-btn:focus,
.logout-btn:focus-visible {
  outline: 2px solid var(--primary-light);
  outline-offset: 2px;
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
  position: relative;
  z-index: 0;
  isolation: isolate;
  width: 100%;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

.main-content__body {
  position: relative;
  z-index: 2;
  min-height: 100%;
}

.main-content::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background: radial-gradient(
    ellipse 90% 65% at 50% -15%,
    rgba(225, 224, 204, 0.06) 0%,
    transparent 52%
  );
}

@media (min-width: 768px) {
  .main-content {
    padding: 1.5rem 1.75rem 3rem;
  }
}

:root.light .main-content::before {
  background: radial-gradient(
    ellipse 90% 60% at 50% -10%,
    rgba(42, 41, 34, 0.05) 0%,
    transparent 50%
  );
}

.footer {
  position: relative;
  z-index: 10;
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
    padding: 0.875rem 1rem 2rem;
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
