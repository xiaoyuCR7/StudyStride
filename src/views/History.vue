<template>
  <div class="history">
    <h1>学习历史</h1>
    <div class="history-container">
      <div class="filters">
        <div class="date-filter">
          <input type="date" v-model="selectedDate" @change="filterByDate" />
          <button @click="showAll">显示全部</button>
        </div>
        <div class="subject-filter">
          <label for="subjectFilter">按科目筛选：</label>
          <select id="subjectFilter" v-model="selectedSubjectFilter" @change="filterBySubject">
            <option value="">-- 全部科目 --</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
              {{ subject.name }}
            </option>
          </select>
        </div>
      </div>
      
      <!-- 学习时长统计 -->
      <div class="stats-container">
        <h2>学习时长统计</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <h3>本周</h3>
            <p class="stat-value">{{ formatDuration(weekTotalTime) }}</p>
          </div>
          <div class="stat-item">
            <h3>本月</h3>
            <p class="stat-value">{{ formatDuration(monthTotalTime) }}</p>
          </div>
          <div class="stat-item">
            <h3>总计</h3>
            <p class="stat-value">{{ formatDuration(totalTotalTime) }}</p>
          </div>
        </div>
      </div>
      
      <!-- 学习时长图表 -->
      <div class="chart-container">
        <h2>学习时长趋势</h2>
        <div class="chart-wrapper">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
      </div>
      
      <div class="sessions-list">
        <h2>{{ displayDate }} 的学习记录</h2>
        <div v-if="filteredSessions.length === 0" class="empty-state">
          暂无学习记录
        </div>
        <div v-else class="session-item" v-for="session in filteredSessions" :key="session.id">
          <div class="session-header">
            <div class="session-time">
              <span v-if="isShowingAll" class="session-date">{{ formatSessionDate(session) }}</span>
              <span class="start-time">{{ formatTime(session.startTime) }}</span>
              <span class="duration">{{ formatDuration(session.duration) }}</span>
            </div>
            <div class="session-actions">
              <div class="session-subject">
                <span class="subject-tag">{{ session.subject || '未分类' }}</span>
              </div>
              <button @click="editSession(session)" class="edit-btn">编辑</button>
              <button @click="showDeleteConfirmModal(session.id)" class="delete-btn">删除</button>
            </div>
          </div>
          <div class="session-content" v-if="session.content">
            {{ session.content }}
          </div>
          <div class="session-content empty" v-else>
            未记录学习内容
          </div>
        </div>
        
        <!-- 编辑会话弹窗 -->
        <div class="modal" v-if="showEditModal">
          <div class="modal-content">
            <h3>编辑学习记录</h3>
            <div class="form-group">
              <label for="editSubject">科目：</label>
              <select id="editSubject" v-model="editSessionData.subject">
                <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
                  {{ subject.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="editDuration">时长：</label>
              <div class="duration-inputs">
                <input type="number" v-model.number="editHours" min="0" placeholder="小时" />
                <span class="separator">:</span>
                <input type="number" v-model.number="editMinutes" min="0" max="59" placeholder="分钟" />
              </div>
            </div>
            <div class="form-group">
              <label for="editContent">内容：</label>
              <textarea id="editContent" v-model="editSessionData.content" placeholder="学习内容..."></textarea>
            </div>
            <div class="modal-buttons">
              <button @click="saveEditedSession">保存</button>
              <button @click="cancelEditSession">取消</button>
            </div>
          </div>
        </div>
        
        <!-- 删除确认弹窗 -->
        <div class="modal" v-if="showDeleteModal">
          <div class="modal-content">
            <h3>确认删除</h3>
            <p class="modal-message">确定要删除这条学习记录吗？此操作不可恢复。</p>
            <div class="modal-buttons">
              <button @click="confirmDeleteSession" class="danger">删除</button>
              <button @click="cancelDeleteSession">取消</button>
            </div>
          </div>
        </div>
        
        <!-- 提示弹窗 -->
        <div class="modal" v-if="showToast">
          <div class="modal-content toast">
            <p class="toast-message">{{ toastMessage }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTimerStore } from '../stores/timer'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const store = useTimerStore()
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedSubjectFilter = ref('')
const filteredSessions = ref<any[]>([])

// 编辑会话相关变量
const showEditModal = ref(false)
const editSessionData = ref({
  id: '',
  subject: '',
  content: '',
  duration: 0
})
const editHours = ref(0)
const editMinutes = ref(0)

// 删除会话相关变量
const showDeleteModal = ref(false)
const deleteSessionId = ref('')

// 提示弹窗相关变量
const showToast = ref(false)
const toastMessage = ref('')

const displayDate = computed(() => {
  const date = selectedDate.value ? new Date(selectedDate.value) : new Date()
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// 是否显示全部学习记录
const isShowingAll = computed(() => {
  return !selectedDate.value
})

// 格式化每条学习记录的日期
const formatSessionDate = (session: any) => {
  if (!session.date) return ''
  const date = new Date(session.date)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

const subjects = computed(() => store.subjects)

// 计算本周总学习时长
const weekTotalTime = computed(() => {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay())
  weekStart.setHours(0, 0, 0, 0)
  const weekStartStr = weekStart.toISOString().split('T')[0] as string
  
  return store.sessions
    .filter(session => session.date >= weekStartStr)
    .reduce((total, session) => total + session.duration, 0)
})

// 计算本月总学习时长
const monthTotalTime = computed(() => {
  const now = new Date()
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
  const monthStartStr = monthStart.toISOString().split('T')[0] as string
  
  return store.sessions
    .filter(session => session.date >= monthStartStr)
    .reduce((total, session) => total + session.duration, 0)
})

// 计算所有时间总学习时长
const totalTotalTime = computed(() => {
  return store.sessions.reduce((total, session) => total + session.duration, 0)
})

// 生成最近7天的日期数组
const getLast7Days = (): string[] => {
  const days: string[] = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    if (dateStr) {
      days.push(dateStr)
    }
  }
  return days
}

// 计算每天的学习时长（分钟）
const dailyStudyMinutes = computed(() => {
  const days = getLast7Days()
  const minutesByDate: Record<string, number> = {}
  
  days.forEach(day => {
    minutesByDate[day] = 0
  })
  
  store.sessions.forEach(session => {
    const date = session.date as string
    if (date && days.includes(date)) {
      if (!minutesByDate[date]) {
        minutesByDate[date] = 0
      }
      minutesByDate[date] += Math.floor(session.duration / 60)
    }
  })
  
  return days.map(day => minutesByDate[day] || 0)
})

// 格式化日期显示 - 显示周几和日期
const formatDateLabel = (dateStr: string): string => {
  const date = new Date(dateStr)
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const weekDay = weekDays[date.getDay()] || ''
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${weekDay}\n${month}/${day}`
}

// 获取当前主题模式
const isLightMode = computed(() => {
  return document.documentElement.classList.contains('light')
})

// 图表数据
const chartData = computed(() => ({
  labels: getLast7Days().map(formatDateLabel),
  datasets: [
    {
      label: '学习时长（分钟）',
      data: dailyStudyMinutes.value,
      backgroundColor: 'rgba(156, 39, 176, 0.6)',
      borderColor: 'rgba(156, 39, 176, 1)',
      borderWidth: 1,
      borderRadius: 8,
      barThickness: 30
    }
  ]
}))

// 图表配置
const chartOptions = computed(() => {
  const textColor = isLightMode.value ? 'rgba(45, 55, 72, 0.8)' : 'rgba(255, 255, 255, 0.8)'
  const gridColor = isLightMode.value ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.1)'
  const tickColor = isLightMode.value ? 'rgba(45, 55, 72, 0.6)' : 'rgba(255, 255, 255, 0.7)'
  
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: textColor,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: {
          color: gridColor
        },
        ticks: {
          color: tickColor,
          callback: function(value: number | string, index: number) {
            const labels = getLast7Days().map(formatDateLabel)
            if (typeof value === 'number' && labels[index]) {
              const parts = labels[index].split('\n')
              return parts
            }
            return ''
          }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: gridColor
        },
        ticks: {
          color: tickColor,
          callback: (value: number | string) => `${value}分钟`
        }
      }
    }
  }
})

const filterSessions = () => {
  let sessions = store.sessions
  
  // 按日期筛选
  if (selectedDate.value) {
    sessions = sessions.filter(session => session.date === selectedDate.value)
  }
  
  // 按科目筛选
  if (selectedSubjectFilter.value) {
    sessions = sessions.filter(session => session.subject === selectedSubjectFilter.value)
  }
  
  filteredSessions.value = sessions
}

const filterByDate = () => {
  filterSessions()
}

const filterBySubject = () => {
  filterSessions()
}

const showAll = () => {
  selectedDate.value = ''
  selectedSubjectFilter.value = ''
  filterSessions()
}

const formatTime = (time: Date | string) => {
  const date = time instanceof Date ? time : new Date(time)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

// 显示删除确认弹窗
const showDeleteConfirmModal = (id: string) => {
  deleteSessionId.value = id
  showDeleteModal.value = true
}

// 确认删除会话
const confirmDeleteSession = async () => {
  if (deleteSessionId.value) {
    store.sessions = store.sessions.filter(session => session.id !== deleteSessionId.value)
    await store.saveSessions()
    filterSessions()
    showToastMessage('学习记录已删除')
    cancelDeleteSession()
  }
}

// 取消删除
const cancelDeleteSession = () => {
  showDeleteModal.value = false
  deleteSessionId.value = ''
}

// 编辑会话
const editSession = (session: any) => {
  editSessionData.value = {
    id: session.id,
    subject: session.subject,
    content: session.content,
    duration: session.duration
  }
  
  // 转换时长为小时和分钟
  editHours.value = Math.floor(session.duration / 3600)
  editMinutes.value = Math.floor((session.duration % 3600) / 60)
  
  showEditModal.value = true
}

// 保存编辑后的会话
const saveEditedSession = async () => {
  const totalSeconds = editHours.value * 3600 + editMinutes.value * 60
  
  if (totalSeconds === 0) {
    showToastMessage('请输入有效的学习时长')
    return
  }
  
  // 找到并更新会话
  const index = store.sessions.findIndex(session => session.id === editSessionData.value.id)
  if (index !== -1) {
    const session = store.sessions[index]
    if (session) {
      const endTime = session.endTime ? new Date(session.endTime) : new Date()
      const startTime = new Date(endTime.getTime() - totalSeconds * 1000)
      
      store.sessions[index] = {
        ...session,
        id: session.id,
        subject: editSessionData.value.subject,
        content: editSessionData.value.content,
        duration: totalSeconds,
        startTime: startTime,
        endTime: endTime,
        date: (session.date || startTime.toISOString().split('T')[0]) as string
      }
      
      await store.saveSessions()
      filterSessions()
      cancelEditSession()
      showToastMessage('学习记录已更新成功')
    }
  }
}

// 取消编辑
const cancelEditSession = () => {
  showEditModal.value = false
  editSessionData.value = {
    id: '',
    subject: '',
    content: '',
    duration: 0
  }
  editHours.value = 0
  editMinutes.value = 0
}

// 显示提示消息
const showToastMessage = (message: string) => {
  toastMessage.value = message
  showToast.value = true
  
  // 2秒后自动关闭
  setTimeout(() => {
    showToast.value = false
  }, 2000)
}

onMounted(async () => {
  await Promise.all([store.loadSessions(), store.loadSubjects()])
  filterSessions()
})
</script>

<style scoped>
.history {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: var(--text-color);
  text-align: center;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
}

.date-filter {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.subject-filter {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.subject-filter label {
  font-size: 1rem;
  color: #333;
  white-space: nowrap;
}

.subject-filter select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  min-width: 150px;
}

input[type="date"] {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  background: #2196F3;
  color: white;
  transition: background-color 0.3s;
}

button:hover {
  opacity: 0.8;
}

.stats-container {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
}

.chart-container {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.stats-container .stat-item {
  background: var(--navbar-user-bg);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  border: 1px solid var(--navbar-user-border);
  transition: all 0.3s ease;
}

.stats-container .stat-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--navbar-item-shadow);
}

.stats-container .stat-item h3 {
  font-size: 1.1rem;
  color: var(--text-color);
  opacity: 0.8;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.stats-container .stat-item .stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sessions-list {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-color);
  opacity: 0.6;
}

.session-item {
  background: var(--navbar-user-bg);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  border: 1px solid var(--navbar-user-border);
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.session-time {
  display: flex;
  gap: 1.5rem;
  font-weight: bold;
  color: var(--text-color);
}

.session-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.session-subject {
  margin-left: auto;
}

.session-date {
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 0.9rem;
  padding-right: 0.5rem;
  border-right: 2px solid var(--card-border);
  margin-right: 0.5rem;
}

.subject-tag {
  background: #4CAF50;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.edit-btn,
.delete-btn {
  padding: 0.25rem 0.75rem;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn {
  background: #2196F3;
  color: white;
}

.delete-btn {
  background: #f44336;
  color: white;
}

.edit-btn:hover,
.delete-btn:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
  cursor: pointer;
}

.modal-content {
  background: var(--card-bg);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  min-width: 450px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  animation: slideInUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  border: 1px solid var(--card-border);
  cursor: default;
}

.modal-content h3 {
  margin-bottom: 2rem;
  background: var(--h1-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}

.modal-message {
  margin-bottom: 2rem;
  color: var(--text-color);
  opacity: 0.8;
  text-align: center;
  line-height: 1.5;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.form-group label {
  font-size: 1rem;
  color: var(--text-color);
  font-weight: 600;
}

.form-group select,
.form-group textarea {
  padding: 1rem;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: var(--navbar-user-bg);
  color: var(--text-color);
}

.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-light);
  background: var(--glass-bg);
  box-shadow: var(--button-hover-shadow);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.duration-inputs {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.duration-inputs input {
  padding: 1rem;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  font-size: 1rem;
  width: 120px;
  text-align: center;
  transition: all 0.3s ease;
  background: var(--navbar-user-bg);
  color: var(--text-color);
}

.duration-inputs input:focus {
  outline: none;
  border-color: var(--primary-light);
  background: var(--glass-bg);
  box-shadow: var(--button-hover-shadow);
}

.duration-inputs .separator {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-color);
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2.5rem;
}

.modal-buttons button {
  padding: 0.875rem 1.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.modal-buttons button:first-child {
  background: #4CAF50;
  color: white;
}

.modal-buttons button:last-child {
  background: #f44336;
  color: white;
}

.modal-buttons button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  opacity: 0.9;
}

.modal-buttons button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 提示弹窗 */
.modal-content.toast {
  min-width: 280px;
  max-width: 400px;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-message {
  text-align: center;
  font-size: 1rem;
  line-height: 1.4;
}

button.danger {
  background: #f44336;
  color: white;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    min-width: 90%;
    padding: 1.5rem;
  }
  
  .duration-inputs {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .duration-inputs input {
    width: 100%;
  }
  
  .duration-inputs .separator {
    display: none;
  }
  
  .modal-buttons {
    flex-direction: column;
  }
  
  .modal-buttons button {
    width: 100%;
  }
  
  .session-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .session-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .session-subject {
    margin-left: 0;
  }
}

.session-content {
  color: var(--text-color);
  opacity: 0.8;
  line-height: 1.5;
}

.session-content.empty {
  font-style: italic;
  color: var(--text-color);
  opacity: 0.5;
}
</style>
