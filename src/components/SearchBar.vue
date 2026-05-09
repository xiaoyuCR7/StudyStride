<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as searchService from '../services/search'
import type { SearchResult } from '../services/search'

const router = useRouter()

const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const isSearching = ref(false)
const showResults = ref(false)
const sortBy = ref<'relevance' | 'date'>('relevance')
const activeFilters = ref<('post' | 'comment' | 'user')[]>(['post', 'comment', 'user'])

const hasResults = computed(() => searchResults.value.length > 0)

const typeLabels: Record<string, string> = {
  post: '帖子',
  comment: '评论',
  user: '用户'
}

async function performSearch() {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  
  isSearching.value = true
  
  try {
    const results = await searchService.search(searchQuery.value, {
      types: activeFilters.value,
      sortBy: sortBy.value,
      limit: 15
    })
    searchResults.value = results
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
}

function goToPost(id: string) {
  router.push(`/community/post/${id}`)
  clearSearch()
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
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

function toggleFilter(type: 'post' | 'comment' | 'user') {
  const index = activeFilters.value.indexOf(type)
  if (index > -1) {
    if (activeFilters.value.length > 1) {
      activeFilters.value.splice(index, 1)
    }
  } else {
    activeFilters.value.push(type)
  }
  if (searchQuery.value.trim()) {
    performSearch()
  }
}

watch(searchQuery, (newVal) => {
  if (newVal.trim()) {
    showResults.value = true
    performSearch()
  } else {
    showResults.value = false
    searchResults.value = []
  }
})
</script>

<template>
  <div class="search-container">
    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <input 
        v-model="searchQuery"
        type="text" 
        placeholder="搜索帖子、评论或用户..."
        class="search-input"
        @focus="showResults = true"
      />
      <button v-if="searchQuery" class="clear-btn" @click="clearSearch">×</button>
    </div>

    <div v-if="showResults" class="search-dropdown">
      <div v-if="!isSearching && searchQuery && !hasResults" class="no-results">
        <p>未找到相关内容</p>
      </div>

      <div v-if="isSearching" class="searching">
        <span class="spinner"></span>
        <span>搜索中...</span>
      </div>

      <div v-if="!isSearching && hasResults" class="results-header">
        <span class="results-count">找到 {{ searchResults.length }} 条结果</span>
        <div class="filter-bar">
          <div class="filter-group">
            <button 
              v-for="type in ['post', 'comment', 'user'] as const" 
              :key="type"
              :class="['filter-btn', { active: activeFilters.includes(type) }]"
              @click="toggleFilter(type)"
            >
              {{ typeLabels[type] }}
            </button>
          </div>
          <select v-model="sortBy" class="sort-select" @change="performSearch">
            <option value="relevance">按相关性</option>
            <option value="date">按时间</option>
          </select>
        </div>
      </div>

      <div v-if="!isSearching && hasResults" class="results-list">
        <div 
          v-for="result in searchResults" 
          :key="result.id"
          class="result-item"
          @click="result.type === 'post' && goToPost(result.id)"
          :class="{ clickable: result.type === 'post' }"
        >
          <div class="result-type">{{ typeLabels[result.type] }}</div>
          <div class="result-content">
            <h4 v-if="result.title" v-html="result.highlight?.title || result.title"></h4>
            <p v-html="result.highlight?.content || result.content"></p>
            <div class="result-meta">
              <span v-if="result.author">{{ result.author }}</span>
              <span>{{ formatDate(result.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-bar {
  display: flex;
  align-items: center;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 25px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.search-bar:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(156, 39, 176, 0.1);
}

.search-icon {
  font-size: 1rem;
  margin-right: 10px;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-color);
  font-size: 1rem;
}

.search-input::placeholder {
  color: var(--text-color);
  opacity: 0.5;
}

.clear-btn {
  background: none;
  border: none;
  color: var(--text-color);
  opacity: 0.6;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: var(--card-hover-shadow);
  max-height: 500px;
  overflow-y: auto;
  z-index: 1000;
}

.no-results, .searching {
  padding: 20px;
  text-align: center;
  color: var(--text-color);
  opacity: 0.6;
}

.searching {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
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

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--card-border);
}

.results-count {
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.7;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 4px;
}

.filter-btn {
  padding: 4px 10px;
  border: 1px solid var(--card-border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-color);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.sort-select {
  padding: 4px 8px;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  background: var(--navbar-user-bg);
  color: var(--text-color);
  font-size: 0.75rem;
  cursor: pointer;
}

.results-list {
  padding: 8px;
}

.result-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.result-item.clickable:hover {
  background: var(--navbar-user-bg);
  cursor: pointer;
}

.result-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  flex-shrink: 0;
}

.result-type:has(.result-item[type="post"]) {
  background: rgba(156, 39, 176, 0.1);
  color: var(--primary-color);
}

.result-type:has(.result-item[type="comment"]) {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.result-type:has(.result-item[type="user"]) {
  background: rgba(255, 152, 0, 0.1);
  color: #FF9800;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.95rem;
  color: var(--text-color);
  font-weight: 500;
}

.result-content p {
  margin: 0 0 6px 0;
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-meta {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--text-color);
  opacity: 0.5;
}

:deep(mark) {
  background: rgba(156, 39, 176, 0.3);
  color: var(--primary-color);
  padding: 1px 3px;
  border-radius: 2px;
}
</style>