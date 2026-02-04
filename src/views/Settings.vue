<template>
  <div class="settings">
    <h1>设置</h1>
    <div class="settings-container">
      <div class="setting-item">
        <h2>休息提醒设置</h2>
        <div class="reminder-setting">
          <label for="reminderInterval">提醒间隔（分钟）：</label>
          <input 
            type="number" 
            id="reminderInterval" 
            v-model.number="reminderInterval" 
            min="1" 
            max="120"
          />
          <button @click="saveSettings">保存设置</button>
        </div>
        <p class="setting-description">
          当学习时长达到设定的分钟数时，系统会发送休息提醒通知
        </p>
      </div>
      
      <div class="setting-item">
        <h2>科目管理</h2>
        <div class="subject-management">
          <div class="add-subject">
            <input 
              type="text" 
              v-model="newSubjectName" 
              placeholder="输入新科目名称"
              @keyup.enter="addSubject"
            />
            <button @click="addSubject">添加科目</button>
          </div>
          <div class="subjects-list">
            <div v-if="subjects.length === 0" class="empty-state">
              暂无科目，请添加
            </div>
            <div v-else class="subject-item" v-for="subject in subjects" :key="subject.id">
              <span class="subject-name">{{ subject.name }}</span>
              <div class="subject-actions">
                <button @click="showEditSubjectModal(subject)" class="edit">编辑</button>
                <button @click="showDeleteConfirmModal(subject.id, subject.name)" class="danger">删除</button>
              </div>
            </div>
          </div>
        </div>
        <p class="setting-description">
          管理您的学习科目，添加新科目或编辑现有科目
        </p>
      </div>
      
      <div class="setting-item">
        <h2>通知权限</h2>
        <div class="notification-setting">
          <button @click="requestNotificationPermission" v-if="notificationPermission === 'default'">
            请求通知权限
          </button>
          <span class="permission-status granted" v-else-if="notificationPermission === 'granted'">
            通知权限已授予
          </span>
          <span class="permission-status denied" v-else-if="notificationPermission === 'denied'">
            通知权限已拒绝
          </span>
        </div>
        <p class="setting-description">
          请授予通知权限以接收休息提醒
        </p>
      </div>
      
      <div class="setting-item">
        <h2>数据管理</h2>
        <div class="data-setting">
          <button @click="exportData">导出数据</button>
          <button @click="importData">导入数据</button>
          <button @click="showClearDataConfirmModal" class="danger">清除数据</button>
        </div>
        <p class="setting-description">
          导出数据将生成一个包含所有学习记录的JSON文件，导入数据将从JSON文件恢复学习记录
        </p>
        <input type="file" id="fileInput" ref="fileInput" style="display: none" accept=".json" @change="handleFileImport" />
      </div>
    </div>
    
    <!-- 编辑科目弹窗 -->
    <div class="modal" v-if="showEditModal">
      <div class="modal-content">
        <h3>编辑科目</h3>
        <input type="text" v-model="editSubjectName" placeholder="输入科目名称" @keyup.enter="confirmEditSubject" />
        <div class="modal-buttons">
          <button @click="confirmEditSubject">确定</button>
          <button @click="cancelEditSubject">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 删除确认弹窗 -->
    <div class="modal" v-if="showDeleteModal">
      <div class="modal-content">
        <h3>确认删除</h3>
        <p class="modal-message">确定要删除科目 "{{ deleteSubjectName }}" 吗？此操作不可恢复。</p>
        <div class="modal-buttons">
          <button @click="confirmDeleteSubject" class="danger">删除</button>
          <button @click="cancelDeleteSubject">取消</button>
        </div>
      </div>
    </div>
    
    <!-- 清除数据确认弹窗 -->
    <div class="modal" v-if="showClearDataModal">
      <div class="modal-content">
        <h3>确认清除数据</h3>
        <p class="modal-message">确定要清除所有学习数据吗？此操作不可恢复。</p>
        <div class="modal-buttons">
          <button @click="confirmClearData" class="danger">清除数据</button>
          <button @click="cancelClearData">取消</button>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTimerStore } from '../stores/timer'

const store = useTimerStore()
const reminderInterval = ref(60)
const notificationPermission = ref('default')
const newSubjectName = ref('')
const editingSubject = ref<any>(null)
const editSubjectName = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// 弹窗相关变量
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const showClearDataModal = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const deleteSubjectId = ref('')
const deleteSubjectName = ref('')

const subjects = computed(() => store.subjects)

const saveSettings = () => {
  store.setReminderInterval(reminderInterval.value)
  showToastMessage('设置已保存')
}

const requestNotificationPermission = () => {
  if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
      notificationPermission.value = permission
      showToastMessage('通知权限已更新')
    })
  }
}

const addSubject = () => {
  if (newSubjectName.value.trim()) {
    store.addSubject(newSubjectName.value.trim())
    showToastMessage('科目添加成功')
    newSubjectName.value = ''
  }
}

// 编辑科目
const showEditSubjectModal = (subject: any) => {
  editingSubject.value = subject
  editSubjectName.value = subject.name
  showEditModal.value = true
}

const confirmEditSubject = () => {
  if (editSubjectName.value.trim() && editingSubject.value) {
    store.updateSubject(editingSubject.value.id, editSubjectName.value.trim())
    showToastMessage('科目更新成功')
    cancelEditSubject()
  }
}

const cancelEditSubject = () => {
  showEditModal.value = false
  editingSubject.value = null
  editSubjectName.value = ''
}

// 删除科目
const showDeleteConfirmModal = (id: string, name: string) => {
  deleteSubjectId.value = id
  deleteSubjectName.value = name
  showDeleteModal.value = true
}

const confirmDeleteSubject = () => {
  if (deleteSubjectId.value) {
    store.removeSubject(deleteSubjectId.value)
    showToastMessage('科目删除成功')
    cancelDeleteSubject()
  }
}

const cancelDeleteSubject = () => {
  showDeleteModal.value = false
  deleteSubjectId.value = ''
  deleteSubjectName.value = ''
}

// 清除数据
const showClearDataConfirmModal = () => {
  showClearDataModal.value = true
}

const confirmClearData = () => {
  localStorage.removeItem('studySessions')
  store.sessions = []
  showToastMessage('数据已清除')
  cancelClearData()
}

const cancelClearData = () => {
  showClearDataModal.value = false
}

const exportData = () => {
  const data = JSON.stringify(store.sessions, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `study-data-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  showToastMessage('数据导出成功')
}

const importData = () => {
  // 触发文件选择
  fileInput.value?.click()
}

const handleFileImport = (event: any) => {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target?.result as string)
      if (Array.isArray(data)) {
        // 验证数据格式
        const isValid = data.every(item => {
          return item.id && item.startTime && item.endTime && item.duration && item.date
        })
        
        if (isValid) {
          // 使用自定义弹窗确认
          if (confirm('确定要导入数据吗？这将覆盖当前的学习记录。')) {
            store.sessions = data
            store.saveSessions()
            showToastMessage('数据导入成功！')
          }
        } else {
          showToastMessage('无效的数据文件格式')
        }
      } else {
        showToastMessage('无效的数据文件格式')
      }
    } catch (error) {
      showToastMessage('数据文件解析失败')
    }
  }
  reader.readAsText(file)
  
  // 重置文件输入，以便可以再次选择同一个文件
  event.target.value = ''
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

onMounted(() => {
  store.loadSettings()
  store.loadSubjects()
  reminderInterval.value = store.reminderInterval
  if ('Notification' in window) {
    notificationPermission.value = Notification.permission
  }
})
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #333;
  text-align: center;
}

.settings-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.setting-item {
  background: #f5f5f5;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.subject-management {
  margin-bottom: 1rem;
}

.add-subject {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.add-subject input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.add-subject input:focus {
  outline: none;
  border-color: #4CAF50;
  background: white;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.subjects-list {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subject-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.subject-item:hover {
  background-color: #f9f9f9;
}

.subject-item:last-child {
  border-bottom: none;
}

.subject-name {
  font-size: 1rem;
  color: #333;
  font-weight: 500;
}

.subject-actions {
  display: flex;
  gap: 0.75rem;
}

.subject-actions button {
  padding: 0.375rem 1rem;
  font-size: 0.85rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subject-actions button.edit {
  background: #2196F3;
  color: white;
}

.subject-actions button.danger {
  background: #f44336;
  color: white;
}

.subject-actions button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  opacity: 0.9;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 6px;
}

.reminder-setting,
.notification-setting,
.data-setting {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

label {
  font-size: 1rem;
  color: #333;
  min-width: 150px;
  font-weight: 500;
}

input[type="number"] {
  padding: 0.75rem;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  font-size: 1rem;
  width: 120px;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

input[type="number"]:focus {
  outline: none;
  border-color: #4CAF50;
  background: white;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background: #2196F3;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  opacity: 0.9;
}

button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

button.danger {
  background: #f44336;
}

.setting-description {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.75rem;
  line-height: 1.4;
}

.permission-status {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
}

.permission-status.granted {
  background: #4CAF50;
  color: white;
}

.permission-status.denied {
  background: #f44336;
  color: white;
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
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  min-width: 350px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  animation: slideInUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: default;
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
}

.modal-content input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.modal-content input:focus {
  outline: none;
  border-color: #4CAF50;
  background: white;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.modal-message {
  margin-bottom: 2rem;
  color: #666;
  text-align: center;
  line-height: 1.5;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.modal-buttons button {
  padding: 0.875rem 1.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
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

@media (max-width: 768px) {
  .settings {
    padding: 1rem;
  }
  
  .add-subject,
  .reminder-setting,
  .notification-setting,
  .data-setting {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  input[type="number"] {
    width: 100%;
  }
  
  button {
    width: 100%;
  }
  
  .subject-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
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
</style>
