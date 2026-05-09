<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as communityService from '../services/community'

const router = useRouter()
const authStore = useAuthStore()

const title = ref('')
const content = ref('')
const postType = ref<'experience' | 'note'>('experience')
const images = ref<string[]>([])
const loading = ref(false)
const errorMessage = ref('')

const forbiddenWords = ['敏感词1', '敏感词2', '敏感词3']

function checkContent(content: string): boolean {
  for (const word of forbiddenWords) {
    if (content.includes(word)) {
      errorMessage.value = '内容包含不当言论，请修改后重试'
      return false
    }
  }
  return true
}

async function handleSubmit() {
  errorMessage.value = ''
  
  if (!title.value.trim()) {
    errorMessage.value = '请输入标题'
    return
  }
  
  if (!content.value.trim()) {
    errorMessage.value = '请输入内容'
    return
  }
  
  if (!checkContent(content.value)) {
    return
  }
  
  loading.value = true
  try {
    await communityService.createPost({
      title: title.value.trim(),
      content: content.value.trim(),
      type: postType.value,
      images: images.value
    })
    
    router.push('/community')
  } catch (error) {
    console.error('发布帖子失败:', error)
    errorMessage.value = '发布失败，请重试'
  } finally {
    loading.value = false
  }
}

function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0 && files[0]) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      if (result) {
        images.value.push(result)
      }
    }
    reader.readAsDataURL(files[0])
  }
}

function removeImage(index: number) {
  images.value.splice(index, 1)
}

function goBack() {
  router.back()
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/login')
  }
})
</script>

<template>
  <div class="create-post-page">
    <button class="back-btn" @click="goBack">← 返回</button>
    
    <h2>发布帖子</h2>
    
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    
    <form class="post-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>帖子类型</label>
        <div class="type-selector">
          <button 
            type="button"
            :class="['type-option', { active: postType === 'experience' }]"
            @click="postType = 'experience'"
          >
            学习经验
          </button>
          <button 
            type="button"
            :class="['type-option', { active: postType === 'note' }]"
            @click="postType = 'note'"
          >
            笔记分享
          </button>
        </div>
      </div>

      <div class="form-group">
        <label>标题</label>
        <input 
          v-model="title"
          type="text" 
          placeholder="请输入帖子标题"
          maxlength="50"
        />
        <span class="char-count">{{ title.length }}/50</span>
      </div>

      <div class="form-group">
        <label>内容</label>
        <textarea 
          v-model="content"
          placeholder="分享你的学习经验或笔记..."
          rows="10"
          maxlength="2000"
        ></textarea>
        <span class="char-count">{{ content.length }}/2000</span>
      </div>

      <div class="form-group">
        <label>图片（可选）</label>
        <input 
          type="file" 
          accept="image/*" 
          @change="handleImageUpload"
          class="image-upload"
        />
        
        <div v-if="images.length > 0" class="preview-images">
          <div 
            v-for="(img, index) in images" 
            :key="index" 
            class="preview-image-item"
          >
            <img :src="img" class="preview-image" />
            <button 
              type="button" 
              class="remove-image-btn"
              @click="removeImage(index)"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? '发布中...' : '发布帖子' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.create-post-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(156, 39, 176, 0.1);
}

.create-post-page h2 {
  font-size: 1.8rem;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 24px;
}

.error-message {
  background: rgba(255, 99, 71, 0.1);
  color: #ff6347;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.post-form {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--card-border);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
}

.type-selector {
  display: flex;
  gap: 12px;
}

.type-option {
  flex: 1;
  padding: 12px;
  border: 1px solid var(--card-border);
  border-radius: 8px;
  background: var(--card-bg);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-option.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--card-border);
  border-radius: 8px;
  background: var(--navbar-user-bg);
  color: var(--text-color);
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
  margin-top: 4px;
}

.image-upload {
  display: block;
  padding: 12px;
  border: 2px dashed var(--card-border);
  border-radius: 8px;
  cursor: pointer;
  background: var(--navbar-user-bg);
}

.image-upload:hover {
  border-color: var(--primary-color);
}

.preview-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
}

.preview-image-item {
  position: relative;
  width: 100px;
  height: 100px;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.remove-image-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  background: #ff6b6b;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-light);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>