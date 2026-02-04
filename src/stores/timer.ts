import { defineStore } from 'pinia'

interface StudySession {
  id: string
  startTime: Date
  endTime: Date | null
  duration: number
  content: string
  date: string
  subject: string
}

interface Subject {
  id: string
  name: string
}

export const useTimerStore = defineStore('timer', {
  state: () => ({
    isRunning: false,
    startTime: null as Date | null,
    elapsedTime: 0,
    currentSession: null as StudySession | null,
    sessions: [] as StudySession[],
    subjects: [] as Subject[],
    selectedSubject: '',
    reminderInterval: 60, // 默认 60 分钟
    lastReminderTime: 0
  }),
  getters: {
    formattedTime: (state) => {
      const totalMinutes = Math.floor(state.elapsedTime / 60)
      const hours = Math.floor(totalMinutes / 60)
      const minutes = totalMinutes % 60
      const seconds = Math.floor(state.elapsedTime % 60)
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    },
    todaySessions: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.sessions.filter(session => session.date === today)
    },
    todayTotalTime: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.sessions.filter(session => session.date === today).reduce((total: number, session: StudySession) => total + session.duration, 0)
    }
  },
  actions: {
    startTimer() {
      if (!this.isRunning) {
        this.isRunning = true
        this.startTime = new Date()
        this.currentSession = {
          id: Date.now().toString(),
          startTime: this.startTime,
          endTime: null,
          duration: 0,
          content: '',
          date: this.startTime.toISOString().split('T')[0] as string,
          subject: this.selectedSubject || '未分类'
        }
      }
    },
    
    // 科目管理方法
    addSubject(name: string) {
      const newSubject: Subject = {
        id: Date.now().toString(),
        name
      }
      this.subjects.push(newSubject)
      this.saveSubjects()
    },
    
    removeSubject(id: string) {
      this.subjects = this.subjects.filter(subject => subject.id !== id)
      this.saveSubjects()
    },
    
    updateSubject(id: string, name: string) {
      const subject = this.subjects.find(subject => subject.id === id)
      if (subject) {
        subject.name = name
        this.saveSubjects()
      }
    },
    
    setSelectedSubject(subject: string) {
      this.selectedSubject = subject
    },
    pauseTimer() {
      if (this.isRunning) {
        this.isRunning = false
        if (this.startTime) {
          const now = new Date()
          this.elapsedTime = Math.floor((now.getTime() - this.startTime.getTime()) / 1000)
          this.startTime = null
        }
      }
    },
    stopTimer() {
      this.pauseTimer()
      if (this.currentSession) {
        this.currentSession.endTime = new Date()
        this.currentSession.duration = this.elapsedTime
        this.sessions.push({ ...this.currentSession })
        this.saveSessions()
        this.resetTimer()
      }
    },
    resetTimer() {
      this.isRunning = false
      this.startTime = null
      this.elapsedTime = 0
      this.currentSession = null
    },
    updateElapsedTime() {
      if (this.isRunning && this.startTime) {
        const now = new Date()
        const totalElapsedSeconds = Math.floor((now.getTime() - this.startTime.getTime()) / 1000)
        this.elapsedTime = totalElapsedSeconds
        
        // 检查是否需要提醒休息
        const totalMinutes = Math.floor(this.elapsedTime / 60)
        if (totalMinutes > 0 && totalMinutes % this.reminderInterval === 0 && totalMinutes !== this.lastReminderTime) {
          this.lastReminderTime = totalMinutes
          this.sendReminder()
        }
      }
    },
    sendReminder() {
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('休息提醒', {
          body: '您已经学习了一段时间，建议休息一下！',
          icon: '/vite.svg'
        })
      }
    },
    saveSessionContent(content: string) {
      if (this.currentSession) {
        this.currentSession.content = content
      }
    },
    saveSessions() {
      localStorage.setItem('studySessions', JSON.stringify(this.sessions))
    },
    loadSessions() {
      const saved = localStorage.getItem('studySessions')
      if (saved) {
        this.sessions = JSON.parse(saved)
      }
    },
    setReminderInterval(interval: number) {
      this.reminderInterval = interval
      localStorage.setItem('reminderInterval', interval.toString())
    },
    loadSettings() {
      const savedInterval = localStorage.getItem('reminderInterval')
      if (savedInterval) {
        this.reminderInterval = parseInt(savedInterval)
      }
    },
    
    // 科目数据持久化
    saveSubjects() {
      localStorage.setItem('studySubjects', JSON.stringify(this.subjects))
    },
    
    loadSubjects() {
      const saved = localStorage.getItem('studySubjects')
      if (saved) {
        this.subjects = JSON.parse(saved)
      } else {
        // 初始为空，用户需要自己添加科目
        this.subjects = []
        this.saveSubjects()
      }
    }
  }
})
