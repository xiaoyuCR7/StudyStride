<template>
  <div class="home">
    <h1>StudyStride</h1>
    <div class="timer-container">
      <div class="subject-selection" v-if="!isRunning && !isPaused">
        <label for="subjectSelect">选择科目：</label>
        <select id="subjectSelect" v-model="selectedSubject" @change="updateSelectedSubject">
          <option value="">-- 请选择科目 --</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
            {{ subject.name }}
          </option>
        </select>
        <button @click="showAddSubjectModal" class="add-subject-btn">添加科目</button>
      </div>
      
      <!-- 添加科目弹窗 -->
      <div class="modal" v-if="showAddSubjectModalFlag">
        <div class="modal-content">
          <h3>添加新科目</h3>
          <input type="text" v-model="newSubjectName" placeholder="输入科目名称" @keyup.enter="addSubject" />
          <div class="modal-buttons">
            <button @click="addSubject">确定</button>
            <button @click="cancelAddSubject">取消</button>
          </div>
        </div>
      </div>
      <div class="current-subject" v-else-if="(isRunning || isPaused) && currentSession">
        <span class="subject-label">当前科目：</span>
        <span class="subject-name">{{ currentSession.subject }}</span>
      </div>
      <div class="timer-display">{{ formattedTime }}</div>
      <div class="timer-buttons">
        <button @click="startTimer" v-if="!isRunning && !isPaused">开始学习</button>
        <button @click="pauseTimer" v-else-if="isRunning">暂停</button>
        <button @click="resumeTimer" v-else-if="isPaused">继续</button>
        <button @click="stopTimer" v-if="isRunning || isPaused">结束</button>
      </div>
    </div>
    
    <div class="content-container" v-if="isRunning || isPaused">
      <h2>学习内容记录</h2>
      <textarea 
        v-model="sessionContent" 
        placeholder="记录今天的学习内容..."
        @input="saveContent"
      ></textarea>
    </div>
    
    <div class="today-summary">
      <h2>今日学习统计</h2>
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">学习次数</span>
          <span class="stat-value">{{ todaySessions.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总时长</span>
          <span class="stat-value">{{ formatDuration(todayTotalTime) }}</span>
        </div>
      </div>
    </div>
    
    <div class="quick-record">
      <h2>快速记录学习</h2>
      <div class="quick-record-form">
        <div class="form-group">
          <label for="quickSubject">选择科目：</label>
          <select id="quickSubject" v-model="quickRecordSubject">
            <option value="">-- 请选择科目 --</option>
            <option v-for="subject in subjects" :key="subject.id" :value="subject.name">
              {{ subject.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="quickDuration">学习时长：</label>
          <div class="duration-inputs">
            <input type="number" id="quickHours" v-model.number="quickRecordHours" min="0" placeholder="小时" />
            <span class="separator">:</span>
            <input type="number" id="quickMinutes" v-model.number="quickRecordMinutes" min="0" max="59" placeholder="分钟" />
          </div>
        </div>
        <div class="form-group">
          <label for="quickContent">学习内容：</label>
          <textarea id="quickContent" v-model="quickRecordContent" placeholder="记录学习内容..."></textarea>
        </div>
        <button @click="recordQuickStudy" class="record-btn">记录学习</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTimerStore } from '../stores/timer'

const store = useTimerStore()
const sessionContent = ref('')
const selectedSubject = ref('')
const newSubjectName = ref('')
const showAddSubjectModalFlag = ref(false)
const isPaused = ref(false)

// 快速记录学习相关变量
const quickRecordSubject = ref('')
const quickRecordHours = ref(0)
const quickRecordMinutes = ref(0)
const quickRecordContent = ref('')

let updateInterval: number | null = null

const isRunning = computed(() => store.isRunning)
const formattedTime = computed(() => store.formattedTime)
const todaySessions = computed(() => store.todaySessions)
const todayTotalTime = computed(() => store.todayTotalTime)
const subjects = computed(() => store.subjects)
const currentSession = computed(() => store.currentSession)

const updateSelectedSubject = () => {
  store.setSelectedSubject(selectedSubject.value)
}

const showAddSubjectModal = () => {
  showAddSubjectModalFlag.value = true
}

const addSubject = () => {
  if (newSubjectName.value.trim()) {
    store.addSubject(newSubjectName.value.trim())
    selectedSubject.value = newSubjectName.value.trim()
    store.setSelectedSubject(selectedSubject.value)
    showAddSubjectModalFlag.value = false
    newSubjectName.value = ''
  }
}

const cancelAddSubject = () => {
  showAddSubjectModalFlag.value = false
  newSubjectName.value = ''
}

const recordQuickStudy = () => {
  if (!quickRecordSubject.value) {
    alert('请选择科目')
    return
  }
  
  const hours = quickRecordHours.value || 0
  const minutes = quickRecordMinutes.value || 0
  const totalSeconds = hours * 3600 + minutes * 60
  
  if (totalSeconds === 0) {
    alert('请输入有效的学习时长')
    return
  }
  
  // 创建快速学习会话
  const now = new Date()
  const session = {
    id: store.newId(),
    startTime: new Date(now.getTime() - totalSeconds * 1000), // 计算开始时间
    endTime: now,
    duration: totalSeconds,
    content: quickRecordContent.value,
    date: now.toISOString().split('T')[0] as string,
    subject: quickRecordSubject.value
  }
  
  // 添加到状态管理
  store.sessions.push(session)
  void store.saveSessions()
  
  // 重置表单
  quickRecordSubject.value = ''
  quickRecordHours.value = 0
  quickRecordMinutes.value = 0
  quickRecordContent.value = ''
  
  alert('学习记录已添加成功！')
}

const startTimer = () => {
  if (!selectedSubject.value) {
    alert('请选择学习科目')
    return
  }
  store.startTimer()
  startUpdateInterval()
  requestNotificationPermission()
}

const pauseTimer = () => {
  store.pauseTimer()
  isPaused.value = true
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

const resumeTimer = () => {
  // 保存当前已用时间
  const currentElapsedTime = store.elapsedTime
  store.startTimer()
  // 调整startTime，确保从暂停的时间继续计算
  if (store.startTime) {
    store.startTime = new Date(store.startTime.getTime() - currentElapsedTime * 1000)
  }
  isPaused.value = false
  startUpdateInterval()
}

const stopTimer = async () => {
  store.saveSessionContent(sessionContent.value)
  await store.stopTimer()
  isPaused.value = false
  sessionContent.value = ''
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = null
  }
}

const saveContent = () => {
  store.saveSessionContent(sessionContent.value)
}

const startUpdateInterval = () => {
  updateInterval = window.setInterval(() => {
    store.updateElapsedTime()
  }, 1000)
}

const requestNotificationPermission = () => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

onMounted(async () => {
  await Promise.all([store.loadSessions(), store.loadSettings(), store.loadSubjects()])
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeIn 1s ease-in-out;
}

.timer-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.timer-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 48px 0 rgba(156, 39, 176, 0.4);
}

.subject-selection {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.subject-selection label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.87);
  font-weight: bold;
}

.subject-selection select {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  min-width: 200px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.87);
  transition: all 0.3s ease;
}

.subject-selection select:hover {
  border-color: #d500f9;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.add-subject-btn {
  padding: 0.75rem 1.5rem;
  background: rgba(156, 39, 176, 0.8);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.add-subject-btn:hover {
  background: rgba(156, 39, 176, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px 0 rgba(156, 39, 176, 0.4);
}

.add-subject-btn:active {
  transform: translateY(1px);
  box-shadow: 0 4px 12px 0 rgba(156, 39, 176, 0.3);
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 16px 48px 0 rgba(156, 39, 176, 0.4);
  min-width: 350px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  animation: slideInUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}

.modal-content input {
  width: 100%;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.87);
}

.modal-content input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.modal-content input:focus {
  outline: none;
  border-color: #d500f9;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(156, 39, 176, 0.3);
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.modal-buttons button {
  padding: 0.875rem 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.modal-buttons button:first-child {
  background: rgba(156, 39, 176, 0.8);
  color: white;
}

.modal-buttons button:last-child {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.modal-buttons button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px 0 rgba(156, 39, 176, 0.4);
  opacity: 1;
}

.modal-buttons button:active {
  transform: translateY(1px);
  box-shadow: 0 4px 12px 0 rgba(156, 39, 176, 0.3);
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

/* 点击背景关闭弹窗 */
.modal {
  cursor: pointer;
}

.modal-content {
  cursor: default;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    min-width: 90%;
    padding: 1.5rem;
  }
  
  .modal-buttons {
    flex-direction: column;
  }
  
  .modal-buttons button {
    width: 100%;
  }
}

.current-subject {
  margin-bottom: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(156, 39, 176, 0.2);
  border-radius: 12px;
  display: inline-block;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.current-subject:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.subject-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-right: 0.5rem;
}

.subject-name {
  font-size: 1rem;
  font-weight: bold;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.timer-display {
  font-size: 4rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'Courier New', monospace;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}

.timer-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

button {
  padding: 0.75rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

button:nth-child(1) {
  background: rgba(156, 39, 176, 0.8);
  color: white;
}

button:nth-child(2) {
  background: rgba(255, 152, 0, 0.8);
  color: white;
}

button:nth-child(3) {
  background: rgba(33, 150, 243, 0.8);
  color: white;
}

button:nth-child(4) {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

button:hover {
  opacity: 1;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px 0 rgba(156, 39, 176, 0.4);
}

button:active {
  transform: translateY(1px);
  box-shadow: 0 4px 12px 0 rgba(156, 39, 176, 0.3);
}

.content-container {
  margin: 2rem 0;
  animation: slideInUp 0.5s ease-out;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  transition: all 0.3s ease;
}

.content-container:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px 0 rgba(156, 39, 176, 0.4);
}

.content-container h2 {
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
}

textarea {
  width: 100%;
  height: 150px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.87);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

textarea:focus {
  outline: none;
  border-color: #d500f9;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(156, 39, 176, 0.3);
}

.today-summary {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-top: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  animation: fadeIn 1s ease-in-out 0.3s both;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.today-summary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px 0 rgba(156, 39, 176, 0.4);
}

.today-summary h2 {
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
}

.stats {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex: 1;
}

.stat-item:hover {
  transform: translateY(-5px);
  background: rgba(156, 39, 176, 0.2);
  box-shadow: 0 8px 24px 0 rgba(156, 39, 176, 0.3);
}

.stat-label {
  display: block;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quick-record {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-top: 2rem;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  animation: fadeIn 1s ease-in-out;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.quick-record:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px 0 rgba(156, 39, 176, 0.4);
}

.quick-record h2 {
  margin-bottom: 1.5rem;
  background: linear-gradient(45deg, #d500f9, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}

.quick-record-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-start;
}

.form-group label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.87);
  font-weight: bold;
}

.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.87);
  transition: all 0.3s ease;
  width: 100%;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.form-group select::placeholder,
.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group select:hover,
.form-group textarea:hover {
  border-color: #d500f9;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.duration-inputs {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.duration-inputs input {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  width: 100px;
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.87);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.duration-inputs input:hover {
  border-color: #d500f9;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
}

.duration-inputs input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.duration-inputs .separator {
  font-size: 1.25rem;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.87);
}

.record-btn {
  background: rgba(156, 39, 176, 0.8);
  color: white;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
  box-shadow: 0 4px 16px 0 rgba(156, 39, 176, 0.3);
  align-self: center;
  min-width: 200px;
}

.record-btn:hover {
  background: rgba(156, 39, 176, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px 0 rgba(156, 39, 176, 0.4);
}

.record-btn:active {
  transform: translateY(1px);
  box-shadow: 0 4px 12px 0 rgba(156, 39, 176, 0.3);
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .timer-display {
    font-size: 3rem;
  }
  
  .timer-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  button {
    width: 200px;
  }
  
  .stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stat-item {
    width: 100%;
  }
  
  .subject-selection {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .subject-selection select {
    width: 100%;
  }
  
  .duration-inputs {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .duration-inputs input {
    width: 100%;
  }
  
  .duration-inputs .separator {
    display: none;
  }
  
  .content-container,
  .today-summary,
  .quick-record,
  .timer-container {
    padding: 1.5rem;
  }
}
</style>
