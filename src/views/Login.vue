<template>
  <div class="login">
    <h1>登录 / 注册</h1>
    <p class="hint">登录后学习记录与科目将同步到 Supabase 云端；未登录时数据仅保存在本机浏览器。</p>
    <form class="login-form" @submit.prevent="onSubmit">
      <div class="field">
        <label for="email">邮箱</label>
        <input id="email" v-model="email" type="email" autocomplete="email" required />
      </div>
      <div class="field">
        <label for="password">密码</label>
        <input id="password" v-model="password" type="password" autocomplete="current-password" required />
      </div>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="infoMessage" class="info">{{ infoMessage }}</p>
      <div class="actions">
        <button type="submit" :disabled="loading">{{ loading ? '处理中…' : '登录' }}</button>
        <button type="button" class="secondary" :disabled="loading" @click="onRegister">注册</button>
      </div>
    </form>
    <router-link to="/" class="back">返回首页</router-link>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email)
}

const onSubmit = async () => {
  errorMessage.value = ''
  infoMessage.value = ''
  
  if (!validateEmail(email.value.trim())) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    return
  }
  
  loading.value = true
  const { error } = await auth.signIn(email.value.trim(), password.value)
  loading.value = false
  if (error) {
    errorMessage.value = error.message
    return
  }
  router.push('/')
}

const onRegister = async () => {
  errorMessage.value = ''
  infoMessage.value = ''
  
  if (!validateEmail(email.value.trim())) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  if (password.value.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    return
  }
  
  loading.value = true
  const { error } = await auth.signUp(email.value.trim(), password.value)
  loading.value = false
  if (error) {
    errorMessage.value = error.message
    return
  }
  infoMessage.value = '若项目开启邮箱验证，请查收邮件后再登录。'
}
</script>

<style scoped>
.login {
  max-width: 420px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

h1 {
  margin-bottom: 0.75rem;
  font-size: 1.75rem;
}

.hint {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.login-form .field {
  margin-bottom: 1rem;
  text-align: left;
}

.login-form label {
  display: block;
  margin-bottom: 0.35rem;
  font-weight: 600;
}

.login-form input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.actions button {
  flex: 1;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  background: #333;
  color: #fff;
}

.actions button.secondary {
  background: #4caf50;
}

.actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #c62828;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.info {
  color: #1565c0;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.back {
  display: inline-block;
  margin-top: 1.5rem;
  color: #333;
}
</style>
