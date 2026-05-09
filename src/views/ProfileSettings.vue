<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as profileService from '../services/profile'
import type { UserProfile, UsernameValidationResult } from '../types/profile'

const router = useRouter()
const authStore = useAuthStore()

const profile = ref<UserProfile | null>(null)
const loading = ref(true)
const saving = ref(false)
const showSuccess = ref(false)

const username = ref('')
const usernameErrors = ref<string[]>([])
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)
const avatarError = ref('')

const isAvatarChanged = ref(false)

async function loadProfile() {
  loading.value = true
  try {
    const data = await profileService.getProfile()
    profile.value = data
    if (data?.username) {
      username.value = data.username
    }
    if (data?.avatarUrl) {
      avatarPreview.value = data.avatarUrl
    }
  } catch (error) {
    console.error('加载资料失败:', error)
  } finally {
    loading.value = false
  }
}

function validateUsernameInput(value: string): UsernameValidationResult {
  return profileService.validateUsername(value)
}

watch(username, (newValue) => {
  if (newValue.trim()) {
    const validation = validateUsernameInput(newValue)
    usernameErrors.value = validation.errors
  } else {
    usernameErrors.value = []
  }
})

function handleAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    avatarError.value = '不支持的文件格式，仅支持 JPG、PNG、GIF'
    return
  }
  
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    avatarError.value = '文件大小超过限制，最大支持5MB'
    return
  }
  
  avatarError.value = ''
  avatarFile.value = file
  isAvatarChanged.value = true
  
  const reader = new FileReader()
  reader.onload = (e) => {
    avatarPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

function removeAvatar() {
  avatarPreview.value = null
  avatarFile.value = null
  avatarError.value = ''
  isAvatarChanged.value = true
}

async function saveChanges() {
  saving.value = true
  showSuccess.value = false
  
  try {
    if (username.value.trim() && username.value !== profile.value?.username) {
      const validation = validateUsernameInput(username.value)
      if (!validation.valid) {
        usernameErrors.value = validation.errors
        saving.value = false
        return
      }
      
      const updated = await profileService.updateUsername(username.value)
      profile.value = updated
    }
    
    if (avatarFile.value) {
      const updated = await profileService.updateAvatar(avatarFile.value)
      profile.value = updated
      avatarFile.value = null
      isAvatarChanged.value = false
    } else if (isAvatarChanged.value && !avatarPreview.value && profile.value?.avatarUrl) {
      const updated = await profileService.deleteAvatar()
      profile.value = updated
      isAvatarChanged.value = false
    }
    
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
    
  } catch (error) {
    console.error('保存失败:', error)
    if (error instanceof Error) {
      if (error.message.includes('用户名')) {
        usernameErrors.value = [error.message]
      } else {
        avatarError.value = error.message
      }
    }
  } finally {
    saving.value = false
  }
}

function getCurrentUsername(): string {
  if (profile.value?.username) {
    return profile.value.username
  }
  return authStore.user?.email?.split('@')[0] || '用户'
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  loadProfile()
})
</script>

<template>
  <div class="profile-settings">
    <div v-if="loading" class="loading">
      <span>加载中...</span>
    </div>

    <div v-else class="settings-content">
      <div class="page-header">
        <h2>个人资料设置</h2>
        <button class="save-btn" @click="saveChanges" :disabled="saving">
          {{ saving ? '保存中...' : '保存更改' }}
        </button>
      </div>

      <div v-if="showSuccess" class="success-message">
        ✓ 资料更新成功！
      </div>

      <div class="profile-section">
        <div class="section-title">头像设置</div>
        
        <div class="avatar-container">
          <div class="avatar-preview">
            <img 
              v-if="avatarPreview" 
              :src="avatarPreview" 
              alt="头像预览"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              <span>{{ getCurrentUsername().charAt(0) }}</span>
            </div>
          </div>
          
          <div class="avatar-actions">
            <label class="upload-btn">
              <input 
                type="file" 
                accept="image/jpeg,image/png,image/gif" 
                @change="handleAvatarChange"
                class="file-input"
              />
              上传头像
            </label>
            <button 
              v-if="avatarPreview || profile?.avatarUrl" 
              class="remove-btn"
              @click="removeAvatar"
            >
              移除头像
            </button>
          </div>
          
          <div v-if="avatarError" class="error-message">{{ avatarError }}</div>
          
          <div class="avatar-hint">
            <span>支持 JPG、PNG、GIF 格式，最大 5MB</span>
          </div>
        </div>
      </div>

      <div class="profile-section">
        <div class="section-title">用户名设置</div>
        
        <div class="form-group">
          <label>显示用户名</label>
          <input 
            v-model="username"
            type="text" 
            placeholder="设置你的显示用户名"
            class="form-input"
          />
          
          <div v-if="usernameErrors.length > 0" class="error-list">
            <span v-for="error in usernameErrors" :key="error" class="error-item">
              × {{ error }}
            </span>
          </div>
          
          <div class="input-hint">
            <span>3-20个字符，仅支持字母、数字和下划线</span>
          </div>
        </div>
        
        <div class="current-username">
          <span class="label">当前用户名：</span>
          <span class="value">{{ getCurrentUsername() }}</span>
        </div>
      </div>

      <div class="profile-section">
        <div class="section-title">账户信息</div>
        
        <div class="info-item">
          <span class="label">邮箱地址：</span>
          <span class="value">{{ authStore.user?.email }}</span>
        </div>
        
        <div class="info-item">
          <span class="label">账户创建时间：</span>
          <span class="value">{{ profile?.createdAt?.toLocaleDateString('zh-CN') }}</span>
        </div>
        
        <div class="info-item">
          <span class="label">最后更新时间：</span>
          <span class="value">{{ profile?.updatedAt?.toLocaleDateString('zh-CN') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-settings {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
}

.settings-content {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 1.5rem;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.save-btn {
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  background: var(--primary-light);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--card-border);
}

.profile-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 16px;
  font-size: 1.1rem;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--card-border);
  background: var(--navbar-user-bg);
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
  background: var(--h1-gradient);
  color: white;
  font-size: 2rem;
  font-weight: bold;
}

.avatar-actions {
  display: flex;
  gap: 12px;
}

.upload-btn {
  padding: 10px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: var(--primary-light);
}

.file-input {
  display: none;
}

.remove-btn {
  padding: 10px 20px;
  background: transparent;
  color: #ff6347;
  border: 1px solid #ff6347;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: rgba(255, 99, 71, 0.1);
}

.avatar-hint {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
}

.error-message {
  color: #ff6347;
  font-size: 0.85rem;
  margin-top: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--card-border);
  border-radius: 8px;
  background: var(--navbar-user-bg);
  color: var(--text-color);
  font-size: 1rem;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.error-list {
  margin-top: 8px;
}

.error-item {
  display: block;
  color: #ff6347;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.input-hint {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
  margin-top: 8px;
}

.current-username, .info-item {
  display: flex;
  gap: 8px;
  font-size: 0.95rem;
}

.current-username .label, .info-item .label {
  color: var(--text-color);
  opacity: 0.6;
}

.current-username .value, .info-item .value {
  color: var(--text-color);
  font-weight: 500;
}
</style>