import { defineStore } from 'pinia'
import { supabase } from '../lib/supabase'
import * as studyData from '../services/studyData'
import type { StudySession, Subject } from '../types/study'

export type { StudySession, Subject }

export const useTimerStore = defineStore('timer', {
  state: () => ({
    isRunning: false,
    startTime: null as Date | null,
    elapsedTime: 0,
    currentSession: null as StudySession | null,
    sessions: [] as StudySession[],
    subjects: [] as Subject[],
    selectedSubject: '',
    reminderInterval: 60,
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
      return state.sessions.filter((session) => session.date === today)
    },
    todayTotalTime: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.sessions
        .filter((session) => session.date === today)
        .reduce((total: number, session: StudySession) => total + session.duration, 0)
    }
  },
  actions: {
    newId() {
      return crypto.randomUUID()
    },

    async loadAll() {
      await Promise.all([this.loadSessions(), this.loadSubjects(), this.loadSettings()])
    },

    startTimer() {
      if (!this.isRunning) {
        this.isRunning = true
        this.startTime = new Date()
        this.currentSession = {
          id: this.newId(),
          startTime: this.startTime,
          endTime: null,
          duration: 0,
          content: '',
          date: this.startTime.toISOString().split('T')[0] as string,
          subject: this.selectedSubject || '未分类'
        }
      }
    },

    addSubject(name: string): { success: boolean; message: string } {
      const trimmedName = name.trim()
      if (!trimmedName) {
        return { success: false, message: '科目名称不能为空' }
      }
      
      const exists = this.subjects.some(
        (s) => s.name.toLowerCase() === trimmedName.toLowerCase()
      )
      if (exists) {
        return { success: false, message: '该科目名称已存在，请使用不同的名称' }
      }
      
      const newSubject: Subject = {
        id: this.newId(),
        name: trimmedName
      }
      this.subjects.push(newSubject)
      void this.saveSubjects()
      return { success: true, message: '科目添加成功' }
    },

    removeSubject(id: string) {
      this.subjects = this.subjects.filter((subject) => subject.id !== id)
      void this.saveSubjects()
    },

    updateSubject(id: string, name: string): { success: boolean; message: string } {
      const trimmedName = name.trim()
      if (!trimmedName) {
        return { success: false, message: '科目名称不能为空' }
      }
      
      const exists = this.subjects.some(
        (s) => s.id !== id && s.name.toLowerCase() === trimmedName.toLowerCase()
      )
      if (exists) {
        return { success: false, message: '该科目名称已存在，请使用不同的名称' }
      }
      
      const subject = this.subjects.find((s) => s.id === id)
      if (subject) {
        subject.name = trimmedName
        void this.saveSubjects()
        return { success: true, message: '科目更新成功' }
      }
      return { success: false, message: '科目不存在' }
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

    async stopTimer() {
      this.pauseTimer()
      if (this.currentSession) {
        this.currentSession.endTime = new Date()
        this.currentSession.duration = this.elapsedTime
        this.sessions.push({ ...this.currentSession })
        await this.saveSessions()
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

        const totalMinutes = Math.floor(this.elapsedTime / 60)
        if (
          totalMinutes > 0 &&
          totalMinutes % this.reminderInterval === 0 &&
          totalMinutes !== this.lastReminderTime
        ) {
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

    async saveSessions() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        this.sessions = await studyData.replaceAllSessions(this.sessions)
        return
      }
      localStorage.setItem('studySessions', JSON.stringify(this.sessions))
    },

    async loadSessions() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        try {
          this.sessions = await studyData.fetchSessions()
        } catch {
          this.sessions = []
        }
        return
      }
      const saved = localStorage.getItem('studySessions')
      if (saved) {
        const parsed = JSON.parse(saved) as Record<string, unknown>[]
        this.sessions = parsed.map((row) => studyData.normalizeSession(row))
      }
    },

    async setReminderInterval(interval: number) {
      this.reminderInterval = interval
      const remote = await studyData.getRemoteSession()
      if (remote) {
        await studyData.upsertUserSettings(interval)
        return
      }
      localStorage.setItem('reminderInterval', interval.toString())
    },

    async loadSettings() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        try {
          const row = await studyData.fetchUserSettings()
          if (row) {
            this.reminderInterval = row.reminder_interval
          }
        } catch {
          /* keep default */
        }
        return
      }
      const savedInterval = localStorage.getItem('reminderInterval')
      if (savedInterval) {
        this.reminderInterval = parseInt(savedInterval, 10)
      }
    },

    async saveSubjects() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        this.subjects = await studyData.replaceAllSubjects(this.subjects)
        return
      }
      localStorage.setItem('studySubjects', JSON.stringify(this.subjects))
    },

    async loadSubjects() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        try {
          this.subjects = await studyData.fetchSubjects()
        } catch {
          this.subjects = []
        }
        return
      }
      const saved = localStorage.getItem('studySubjects')
      if (saved) {
        this.subjects = JSON.parse(saved)
      } else {
        this.subjects = []
        localStorage.setItem('studySubjects', JSON.stringify(this.subjects))
      }
    },

    async clearAllSessions() {
      const remote = await studyData.getRemoteSession()
      if (remote) {
        const userId = (await supabase.auth.getUser()).data.user?.id
        if (userId) {
          await supabase.from('study_sessions').delete().eq('user_id', userId)
        }
      }
      this.sessions = []
      localStorage.removeItem('studySessions')
    }
  }
})
