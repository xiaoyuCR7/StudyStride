import { defineStore } from 'pinia'
import type { Session, User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { useTimerStore } from './timer'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    session: null as Session | null,
    user: null as User | null,
    initialized: false
  }),
  getters: {
    isLoggedIn: (s) => !!s.session
  },
  actions: {
    async init() {
      const { data: { session } } = await supabase.auth.getSession()
      this.session = session
      this.user = session?.user ?? null
      
      if (session && !this.initialized) {
        await useTimerStore().loadAll()
      }
      
      this.initialized = true

      supabase.auth.onAuthStateChange(async (event, session) => {
        console.log('认证状态变化:', { event, session })
        this.session = session
        this.user = session?.user ?? null
        console.log('状态已更新:', { session: this.session, user: this.user, isLoggedIn: !!this.session })
        if (event === 'SIGNED_IN') {
          await useTimerStore().loadAll()
        } else if (event === 'SIGNED_OUT') {
          useTimerStore().$reset()
        }
      })
    },
    async signIn(email: string, password: string) {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      return { error }
    },
    async signUp(email: string, password: string) {
      const { error } = await supabase.auth.signUp({ email, password })
      return { error }
    },
    async signOut() {
      try {
        console.log('开始执行退出登录')
        // 先清除本地状态
        this.session = null
        this.user = null
        console.log('本地状态已重置')
        
        const { error } = await supabase.auth.signOut({})
        if (error) {
          console.error('退出登录失败:', error)
        } else {
          console.log('退出登录成功')
        }
      } catch (error) {
        console.error('退出登录异常:', error)
        // 即使出错也确保状态被重置
        this.session = null
        this.user = null
      }
      console.log('退出登录完成，最终状态:', { session: this.session, user: this.user, isLoggedIn: !!this.session })
    }
  }
})
