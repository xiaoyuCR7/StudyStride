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
// App component
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
