<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as communityService from '../services/community'
import type { CommunityPost, CommunityComment } from '../types/community'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const post = ref<CommunityPost | null>(null)
const comments = ref<CommunityComment[]>([])
const loading = ref(true)
const commentContent = ref('')
const showDeleteConfirm = ref(false)
const errorMessage = ref('')
const isSubmitting = ref(false)

const postId = computed(() => route.params.id as string)

const canDelete = computed(() => {
  if (!post.value || !authStore.user) return false
  return post.value.userId === authStore.user.id
})

async function loadPost() {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await communityService.fetchPostById(postId.value)
    post.value = data
    if (data) {
      await loadComments()
    }
  } catch (error) {
    console.error('加载帖子失败:', error)
    errorMessage.value = '加载帖子失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  try {
    comments.value = await communityService.fetchComments(postId.value)
  } catch (error) {
    console.error('加载评论失败:', error)
    errorMessage.value = '加载评论失败'
  }
}

async function handleLike() {
  if (!post.value || isSubmitting.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    const result = await communityService.toggleLike(post.value.id)
    if (post.value) {
      post.value.likes = result.count
      post.value.isLiked = result.liked
    }
  } catch (error) {
    console.error('点赞失败:', error)
    errorMessage.value = '操作失败，请稍后重试'
  } finally {
    isSubmitting.value = false
  }
}

async function handleComment() {
  if (!commentContent.value.trim() || !post.value || isSubmitting.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    const newComment = await communityService.createComment(post.value.id, commentContent.value.trim())
    comments.value.push(newComment)
    commentContent.value = ''
    if (post.value) {
      post.value.commentsCount++
    }
  } catch (error) {
    console.error('发布评论失败:', error)
    errorMessage.value = '发布评论失败，请稍后重试'
  } finally {
    isSubmitting.value = false
  }
}

async function handleDeletePost() {
  if (!post.value || isSubmitting.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    await communityService.deletePost(post.value.id)
    router.push('/community')
  } catch (error) {
    console.error('删除帖子失败:', error)
    errorMessage.value = '删除失败，请稍后重试'
    showDeleteConfirm.value = false
  } finally {
    isSubmitting.value = false
  }
}

function formatDate(date: Date): string {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function goBack() {
  router.back()
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  loadPost()
})
</script>

<template>
  <div class="post-detail-page">
    <button class="back-btn" @click="goBack">← 返回</button>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div v-if="loading" class="loading">
      <span>加载中...</span>
    </div>

    <div v-else-if="post" class="post-container">
      <div class="post-header">
        <div class="author-info">
          <div class="avatar">{{ post.userName.charAt(0) }}</div>
          <div class="author-meta">
            <span class="author-name">{{ post.userName }}</span>
            <span class="post-time">{{ formatDate(post.createdAt) }}</span>
          </div>
        </div>
        <div class="post-header-right">
          <span :class="['type-badge', post.type]">
            {{ post.type === 'experience' ? '经验分享' : '学习笔记' }}
          </span>
          <button 
            v-if="canDelete" 
            class="delete-post-btn" 
            @click="showDeleteConfirm = true"
            :disabled="isSubmitting"
          >
            删除
          </button>
        </div>
      </div>

      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-content">{{ post.content }}</div>

      <div v-if="post.images && post.images.length > 0" class="post-images">
        <img 
          v-for="(img, index) in post.images" 
          :key="index" 
          :src="img" 
          class="post-image"
        />
      </div>

      <div class="post-actions">
        <button 
          :class="['like-btn', { liked: post.isLiked }]"
          @click="handleLike"
          :disabled="isSubmitting"
        >
          <span class="icon">♥</span>
          <span>{{ post.likes }}</span>
        </button>
        <div class="comments-section">
          <h3>评论 ({{ post.commentsCount }})</h3>
          
          <div class="comment-input">
            <input 
              v-model="commentContent"
              type="text" 
              placeholder="写下你的评论..."
              @keyup.enter="handleComment"
              :disabled="isSubmitting"
            />
            <button @click="handleComment" :disabled="isSubmitting">
              {{ isSubmitting ? '发送中...' : '发送' }}
            </button>
          </div>

          <div class="comments-list">
            <div 
              v-for="comment in comments" 
              :key="comment.id" 
              class="comment-item"
            >
              <div class="comment-author">
                <div class="avatar-small">{{ comment.userName.charAt(0) }}</div>
                <div class="comment-meta">
                  <span class="comment-author-name">{{ comment.userName }}</span>
                  <span class="comment-time">{{ formatDate(comment.createdAt) }}</span>
                </div>
              </div>
              <p class="comment-content">{{ comment.content }}</p>
            </div>

            <div v-if="comments.length === 0" class="empty-comments">
              <p>暂无评论，来发表第一条评论吧！</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <p>帖子不存在或已被删除</p>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal">
        <h3>确认删除</h3>
        <p>确定要删除这篇帖子吗？此操作无法撤销。</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteConfirm = false" :disabled="isSubmitting">取消</button>
          <button class="delete-btn" @click="handleDeletePost" :disabled="isSubmitting">
            {{ isSubmitting ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-detail-page {
  max-width: 800px;
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

.error-message {
  background: rgba(255, 99, 71, 0.1);
  color: #ff6347;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.loading, .not-found {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
}

.post-container {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--card-border);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.post-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.delete-post-btn {
  padding: 6px 12px;
  background: rgba(255, 99, 71, 0.1);
  border: 1px solid #ff6347;
  border-radius: 6px;
  color: #ff6347;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-post-btn:hover:not(:disabled) {
  background: #ff6347;
  color: white;
}

.delete-post-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--h1-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--h1-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8rem;
}

.author-meta {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: var(--text-color);
}

.post-time {
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.6;
}

.type-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.type-badge.experience {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.type-badge.note {
  background: rgba(255, 193, 7, 0.1);
  color: #FFC107;
}

.post-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 16px;
}

.post-content {
  color: var(--text-color);
  line-height: 1.8;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.post-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
}

.post-actions {
  border-top: 1px solid var(--card-border);
  padding-top: 20px;
}

.like-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  padding: 10px 20px;
  border-radius: 25px;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.like-btn:hover:not(:disabled) {
  background: rgba(255, 182, 193, 0.2);
}

.like-btn.liked {
  background: rgba(255, 182, 193, 0.3);
  color: #ff6b6b;
}

.like-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comments-section h3 {
  color: var(--text-color);
  margin-bottom: 16px;
}

.comment-input {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.comment-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--card-border);
  border-radius: 25px;
  background: var(--card-bg);
  color: var(--text-color);
  font-size: 1rem;
}

.comment-input input:disabled {
  opacity: 0.5;
}

.comment-input button {
  padding: 12px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.comment-input button:hover:not(:disabled) {
  background: var(--primary-light);
}

.comment-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  background: var(--navbar-user-bg);
  padding: 16px;
  border-radius: 8px;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.comment-meta {
  display: flex;
  flex-direction: column;
}

.comment-author-name {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.9rem;
}

.comment-time {
  font-size: 0.75rem;
  color: var(--text-color);
  opacity: 0.5;
}

.comment-content {
  color: var(--text-color);
  opacity: 0.8;
  font-size: 0.95rem;
}

.empty-comments {
  text-align: center;
  padding: 30px;
  color: var(--text-color);
  opacity: 0.5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: var(--card-bg);
  padding: 24px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
}

.modal h3 {
  color: var(--text-color);
  margin-bottom: 12px;
}

.modal p {
  color: var(--text-color);
  opacity: 0.8;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 8px 16px;
  background: var(--navbar-user-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  color: var(--text-color);
  cursor: pointer;
}

.cancel-btn:disabled {
  opacity: 0.5;
}

.delete-btn {
  padding: 8px 16px;
  background: #ff6b6b;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.delete-btn:disabled {
  opacity: 0.5;
}
</style>