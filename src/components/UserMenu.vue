<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as profileService from '../services/profile'
import type { UserProfile } from '../types/profile'

const router = useRouter()
const auth = useAuthStore()

const isOpen = ref(false)
const profile = ref<UserProfile | null>(null)
const loading = ref(false)
const triggerRect = ref({ top: 0, left: 0, width: 0, height: 0 })
const triggerRef = ref<HTMLElement | null>(null)

async function loadProfile() {
  loading.value = true
  try {
    const data = await profileService.getProfile()
    profile.value = data
  } catch (error) {
    console.error('加载用户资料失败:', error)
  } finally {
    loading.value = false
  }
}

function updateDropdownPosition() {
  if (triggerRef.value) {
    const rect = triggerRef.value.getBoundingClientRect()
    triggerRect.value = rect
  }
}

function toggleMenu() {
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  isOpen.value = !isOpen.value
  
  if (isOpen.value) {
    nextTick(() => {
      updateDropdownPosition()
    })
  }
}

function closeMenu() {
  isOpen.value = false
}

function goToProfile() {
  router.push('/profile')
  closeMenu()
}

function goToSettings() {
  router.push('/settings')
  closeMenu()
}

const isLoggingOut = ref(false)

async function logout() {
  if (isLoggingOut.value) {
    console.log('正在退出登录中，请稍候...')
    return
  }
  
  console.log('点击退出登录按钮')
  closeMenu()
  
  isLoggingOut.value = true
  try {
    console.log('开始执行 signOut')
    await auth.signOut()
    console.log('signOut 执行完成，准备跳转到登录页')
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    alert('退出登录失败，请刷新页面重试')
  } finally {
    isLoggingOut.value = false
  }
}

function getDisplayUsername(): string {
  if (profile.value?.username) {
    return profile.value.username
  }
  return auth.user?.email?.split('@')[0] || '用户'
}

function hasAvatar(): boolean {
  return !loading.value && profile.value?.avatarUrl !== undefined && profile.value?.avatarUrl !== null
}

const dropdownStyle = computed(() => ({
  position: 'fixed' as const,
  top: `${triggerRect.value.top + triggerRect.value.height + 8}px`,
  right: `${window.innerWidth - triggerRect.value.left - triggerRect.value.width + 20}px`,
  zIndex: 9999
}))

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu-container') && !target.closest('.user-dropdown-teleport')) {
    closeMenu()
  }
}

function handleResize() {
  if (isOpen.value) {
    updateDropdownPosition()
  }
}

watch(isOpen, (newVal) => {
  if (newVal) {
    updateDropdownPosition()
  }
})

onMounted(() => {
  if (auth.isLoggedIn) {
    loadProfile()
  }
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="user-menu-container">
    <button 
      ref="triggerRef"
      class="user-menu-trigger" 
      @click.stop="toggleMenu"
      :class="{ 'not-logged-in': !auth.isLoggedIn, 'no-avatar': auth.isLoggedIn && !hasAvatar() }"
    >
      <div class="user-avatar">
        <img 
          v-if="hasAvatar()" 
          :src="profile?.avatarUrl || undefined" 
          :alt="getDisplayUsername()"
          class="avatar-image"
        />
        <span v-else class="avatar-placeholder">
          {{ getDisplayUsername().charAt(0) }}
        </span>
      </div>
      
      <span v-if="auth.isLoggedIn" class="user-info">
        <span class="user-name">{{ getDisplayUsername() }}</span>
      </span>
      
      <span v-if="auth.isLoggedIn" class="menu-arrow" :class="{ open: isOpen }">▼</span>
    </button>

    <Teleport to="body">
      <Transition name="dropdown">
        <div 
          v-if="isOpen" 
          class="user-dropdown-teleport"
          :style="dropdownStyle"
        >
          <div class="user-dropdown">
            <div class="dropdown-header">
              <div class="dropdown-avatar">
                <img 
                  v-if="hasAvatar()" 
                  :src="profile?.avatarUrl || undefined" 
                  :alt="getDisplayUsername()"
                  class="dropdown-avatar-image"
                />
                <span v-else class="dropdown-avatar-placeholder">
                  {{ getDisplayUsername().charAt(0) }}
                </span>
              </div>
              <div class="dropdown-user-info">
                <span class="dropdown-user-name">{{ getDisplayUsername() }}</span>
              </div>
            </div>

            <div class="dropdown-divider"></div>

            <div class="dropdown-items">
              <button class="dropdown-item" @click="goToProfile">
                <span class="item-icon">👤</span>
                <span class="item-text">个人资料</span>
              </button>
              <button class="dropdown-item" @click="goToSettings">
                <span class="item-icon">⚙️</span>
                <span class="item-text">设置</span>
              </button>
            </div>

            <div class="dropdown-divider"></div>

            <button class="dropdown-item logout" @click="logout">
              <span class="item-icon">🚪</span>
              <span class="item-text">退出登录</span>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.user-menu-container {
  position: relative;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--navbar-user-bg);
  border: 1px solid var(--navbar-user-border);
  border-radius: 12px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color);
  font-family: inherit;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 100;
}

.user-menu-trigger:hover {
  border-color: var(--primary-light);
  box-shadow: var(--navbar-item-shadow);
  transform: translateY(-1px);
}

.user-menu-trigger.not-logged-in,
.user-menu-trigger.no-avatar {
  padding: 8px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #9ca3af;
  color: #ffffff;
  font-size: 1rem;
  font-weight: bold;
}

.user-menu-trigger.not-logged-in .avatar-placeholder,
.user-menu-trigger.no-avatar .avatar-placeholder {
  background: #9ca3af;
  color: #ffffff;
}

.user-menu-trigger:not(.not-logged-in):not(.no-avatar) .avatar-placeholder {
  background: var(--h1-gradient);
  color: white;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.menu-arrow {
  font-size: 0.7rem;
  opacity: 0.6;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.menu-arrow.open {
  transform: rotate(180deg);
}

.user-dropdown-teleport {
  width: 240px;
}

.user-dropdown {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: var(--card-hover-shadow);
  overflow: hidden;
  animation: dropdownFadeIn 0.2s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--navbar-user-bg);
}

.dropdown-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.dropdown-avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #9ca3af;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: bold;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dropdown-user-name {
  font-weight: 600;
  color: var(--text-color);
}

.dropdown-divider {
  height: 1px;
  background: var(--card-border);
}

.dropdown-items {
  padding: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color);
  font-family: inherit;
  font-size: 0.9rem;
  transition: background 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--navbar-user-bg);
}

.dropdown-item.logout {
  color: #ff6347;
}

.dropdown-item.logout:hover {
  background: rgba(255, 99, 71, 0.1);
}

.item-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.item-text {
  flex: 1;
}

@media (max-width: 768px) {
  .user-menu-trigger {
    padding: 6px 8px;
  }

  .user-info {
    display: none;
  }

  .user-dropdown-teleport {
    width: calc(100vw - 20px);
    right: 10px !important;
  }
}
</style>