<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as communityService from '../services/community'
import type { CommunityPost } from '../types/community'
import { useIntersectionObserver } from '@vueuse/core'
import SearchBar from '../components/SearchBar.vue'

const router = useRouter()
const authStore = useAuthStore()

const posts = ref<CommunityPost[]>([])
const currentPage = ref(1)
const pageSize = 20
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const activeType = ref<'all' | 'experience' | 'note'>('all')
const skeletonCount = ref(6)
const showSkeleton = ref(true)
const observerRef = ref<HTMLElement | null>(null)

const filteredPosts = computed(() => {
  if (activeType.value === 'all') return posts.value
  return posts.value.filter(p => p.type === activeType.value)
})

async function loadPosts(page: number = 1) {
  if ((page > 1 && loadingMore.value) || (page === 1 && loading.value)) return
  
  if (page === 1) {
    loading.value = true
  } else {
    loadingMore.value = true
  }
  
  try {
    const startTime = performance.now()
    const type = activeType.value === 'all' ? undefined : activeType.value
    const newPosts = await communityService.fetchPosts(page, pageSize, type)
    const loadTime = performance.now() - startTime
    
    console.log(`[Performance] Loaded ${newPosts.length} posts in ${loadTime.toFixed(2)}ms (Page ${page})`)
    
    if (newPosts.length < pageSize) {
      hasMore.value = false
    }
    if (page === 1) {
      posts.value = newPosts
      showSkeleton.value = false
    } else {
      posts.value = [...posts.value, ...newPosts]
    }
  } catch (error) {
    console.error('加载帖子失败:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  if (hasMore.value && !loading.value && !loadingMore.value) {
    currentPage.value++
    loadPosts(currentPage.value)
  }
}

function formatDate(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

function goToPostDetail(postId: string) {
  router.push(`/community/post/${postId}`)
}

function goToCreatePost() {
  router.push('/community/post/create')
}

function setActiveType(type: 'all' | 'experience' | 'note') {
  activeType.value = type
  currentPage.value = 1
  hasMore.value = true
  showSkeleton.value = true
  loadPosts(1)
}

function setupInfiniteScroll() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && hasMore.value && !loading.value && !loadingMore.value) {
          loadMore()
        }
      })
    },
    {
      rootMargin: '200px',
      threshold: 0.1
    }
  )
  
  if (observerRef.value) {
    observer.observe(observerRef.value)
  }
  
  return observer
}

let scrollObserver: IntersectionObserver | null = null

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  const startTime = performance.now()
  
  loadPosts(1).then(() => {
    const totalTime = performance.now() - startTime
    console.log(`[Performance] Initial load completed in ${totalTime.toFixed(2)}ms`)
  })
  
  scrollObserver = setupInfiniteScroll()
})

onUnmounted(() => {
  if (scrollObserver) {
    scrollObserver.disconnect()
  }
})

const postImages = ref<Map<string, { loaded: boolean; src: string }>>(new Map())

function useLazyImage(el: HTMLElement | null, src: string) {
  if (!el) return
  
  const imageData = postImages.value.get(src) || { loaded: false, src }
  postImages.value.set(src, imageData)
  
  useIntersectionObserver(el, (entries) => {
    const entry = entries[0]
    if (entry?.isIntersecting && !imageData.loaded) {
      imageData.loaded = true
      el.setAttribute('src', src)
    }
  }, {
    rootMargin: '100px',
    threshold: 0.01
  })
}
</script>

<template>
  <div class="community-page">
    <div class="community-header">
      <h2>学习社区</h2>
      <div class="header-actions">
        <SearchBar />
        <button class="create-btn" @click="goToCreatePost">发布帖子</button>
      </div>
    </div>

    <div class="filter-tabs">
      <button 
        :class="['tab', { active: activeType === 'all' }]"
        @click="setActiveType('all')"
      >
        全部
      </button>
      <button 
        :class="['tab', { active: activeType === 'experience' }]"
        @click="setActiveType('experience')"
      >
        学习经验
      </button>
      <button 
        :class="['tab', { active: activeType === 'note' }]"
        @click="setActiveType('note')"
      >
        笔记分享
      </button>
    </div>

    <div v-if="showSkeleton" class="posts-list skeleton-list">
      <div v-for="i in skeletonCount" :key="i" class="skeleton-card">
        <div class="skeleton-header">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-meta">
            <div class="skeleton-line short"></div>
            <div class="skeleton-line tiny"></div>
          </div>
          <div class="skeleton-badge"></div>
        </div>
        <div class="skeleton-title"></div>
        <div class="skeleton-content">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
        <div class="skeleton-images" v-if="i % 3 === 0">
          <div class="skeleton-image"></div>
          <div class="skeleton-image"></div>
          <div class="skeleton-image"></div>
        </div>
        <div class="skeleton-footer">
          <div class="skeleton-interaction"></div>
          <div class="skeleton-interaction"></div>
        </div>
      </div>
    </div>

    <div v-else class="posts-list">
      <div 
        v-for="post in filteredPosts" 
        :key="post.id" 
        class="post-card"
        @click="goToPostDetail(post.id)"
      >
        <div class="post-header">
          <div class="author-info">
            <div class="avatar">
              <img v-if="post.userAvatar" :src="post.userAvatar" :alt="post.userName" class="avatar-image" />
              <span v-else>{{ post.userName.charAt(0) }}</span>
            </div>
            <div class="author-meta">
              <span class="author-name">{{ post.userName }}</span>
              <span class="post-time">{{ formatDate(post.createdAt) }}</span>
            </div>
          </div>
          <span :class="['type-badge', post.type]">
            {{ post.type === 'experience' ? '经验分享' : '学习笔记' }}
          </span>
        </div>

        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-content">{{ post.content.slice(0, 120) }}{{ post.content.length > 120 ? '...' : '' }}</p>

        <div v-if="post.images && post.images.length > 0" class="post-images">
          <img 
            v-for="(img, index) in post.images.slice(0, 3)" 
            :key="index" 
            :data-src="img"
            class="post-image lazy"
            :ref="(el) => useLazyImage(el as HTMLElement, img)"
            :alt="`图片${index + 1}`"
          />
        </div>

        <div class="post-footer">
          <button class="interaction-btn" @click.stop>
            <span class="icon">♥</span>
            <span>{{ post.likes }}</span>
          </button>
          <button class="interaction-btn" @click.stop>
            <span class="icon">💬</span>
            <span>{{ post.commentsCount }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loadingMore" class="loading-more">
      <div class="spinner"></div>
      <span>加载更多...</span>
    </div>

    <div v-if="!loading && !loadingMore && !hasMore && posts.length > 0" class="no-more">
      <p>已加载全部内容</p>
    </div>

    <div v-if="!loading && !showSkeleton && posts.length === 0" class="empty-state">
      <p>暂无帖子，快来发布第一篇吧！</p>
    </div>

    <div ref="observerRef" class="scroll-trigger"></div>
  </div>
</template>

<style scoped>
.community-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  position: sticky;
  top: 0;
  background: var(--page-bg);
  z-index: 100;
  padding: 10px 0;
  flex-wrap: wrap;
  gap: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.community-header h2 {
  font-size: 1.8rem;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.create-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.create-btn:hover {
  background: var(--primary-light);
  transform: translateY(-1px);
}

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tab {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  background: var(--card-bg);
  color: var(--text-color);
  transition: all 0.2s ease;
}

.tab.active {
  background: var(--primary-color);
  color: white;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-list {
  pointer-events: none;
}

.skeleton-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--card-border);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-meta {
  flex: 1;
  margin-left: 12px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-line.tiny {
  width: 40%;
  height: 12px;
}

.skeleton-badge {
  width: 60px;
  height: 24px;
  border-radius: 12px;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-title {
  height: 24px;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-content {
  margin-bottom: 12px;
}

.skeleton-images {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.skeleton-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-footer {
  display: flex;
  gap: 24px;
}

.skeleton-interaction {
  width: 40px;
  height: 16px;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--card-border) 25%, var(--navbar-user-bg) 50%, var(--card-border) 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.post-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--card-border);
  will-change: transform;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-hover-shadow);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--h1-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.author-meta {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
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
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
  line-height: 1.4;
}

.post-content {
  color: var(--text-color);
  opacity: 0.8;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.post-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  background: var(--card-border);
  transition: opacity 0.3s ease;
}

.post-image.lazy {
  opacity: 0;
}

.post-image.lazy[src] {
  opacity: 1;
}

.post-footer {
  display: flex;
  gap: 24px;
}

.interaction-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.7;
  cursor: pointer;
  transition: all 0.2s ease;
}

.interaction-btn:hover {
  opacity: 1;
}

.icon {
  font-size: 1rem;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--card-border);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.no-more, .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-color);
  opacity: 0.6;
}

.scroll-trigger {
  height: 1px;
  margin-top: 20px;
}
</style>