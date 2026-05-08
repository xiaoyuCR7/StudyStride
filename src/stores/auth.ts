import { defineStore } from 'pinia'
import type { Session, User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { useTimerStore } from './timer'

const RETRY_DELAY = 1000
const MAX_RETRIES = 3

async function withRetry<T>(fn: () => Promise<T>, retries: number = MAX_RETRIES): Promise<T> {
  let lastError: Error | null = null
  
  for (let i = 0; i < retries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      console.warn(`操作失败，重试 ${i + 1}/${retries}:`, lastError.message)
      
      if (i < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)))
      }
    }
  }
  
  throw lastError || new Error('操作失败，已达到最大重试次数')
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    session: null as Session | null,
    user: null as User | null,
    initialized: false,
    isLoading: false
  }),
  getters: {
    isLoggedIn: (s) => !!s.session
  },
  actions: {
    async init() {
      if (this.initialized) return
      
      this.isLoading = true
      try {
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) {
          console.error('初始化会话失败:', error)
        } else {
          this.session = session
          this.user = session?.user ?? null
          
          if (session) {
            try {
              await useTimerStore().loadAll()
            } catch (loadError) {
              console.error('加载用户数据失败:', loadError)
            }
          }
        }
        
        supabase.auth.onAuthStateChange(async (event, session) => {
          console.log('认证状态变化:', { event, session })
          this.session = session
          this.user = session?.user ?? null
          
          try {
            if (event === 'SIGNED_IN') {
              await useTimerStore().loadAll()
            } else if (event === 'SIGNED_OUT') {
              useTimerStore().$reset()
            }
          } catch (error) {
            console.error('认证状态变化处理失败:', error)
          }
        })
      } catch (error) {
        console.error('认证初始化异常:', error)
      } finally {
        this.initialized = true
        this.isLoading = false
      }
    },
    
    async signIn(email: string, password: string) {
      if (!email || !password) {
        return { error: new Error('邮箱和密码不能为空') }
      }
      
      this.isLoading = true
      try {
        const result = await withRetry(async () => {
          return await supabase.auth.signInWithPassword({ email, password })
        })
        
        if (result.error) {
          console.error('登录失败:', result.error)
          return { error: result.error }
        }
        
        this.session = result.data.session
        this.user = result.data.user
        console.log('登录成功:', { session: this.session, user: this.user })
        
        try {
          await useTimerStore().loadAll()
        } catch (loadError) {
          console.error('登录后加载数据失败:', loadError)
        }
        
        return { error: null }
      } catch (error) {
        console.error('登录异常:', error)
        return { error: error instanceof Error ? error : new Error('登录失败') }
      } finally {
        this.isLoading = false
      }
    },
    
    async signUp(email: string, password: string) {
      if (!email || !password) {
        return { error: new Error('邮箱和密码不能为空') }
      }
      
      if (password.length < 6) {
        return { error: new Error('密码长度至少需要6位') }
      }
      
      this.isLoading = true
      try {
        const result = await withRetry(async () => {
          return await supabase.auth.signUp({ email, password })
        })
        
        if (result.error) {
          console.error('注册失败:', result.error)
          return { error: result.error }
        }
        
        this.session = result.data.session
        this.user = result.data.user
        console.log('注册成功:', { session: this.session, user: this.user })
        
        return { error: null }
      } catch (error) {
        console.error('注册异常:', error)
        return { error: error instanceof Error ? error : new Error('注册失败') }
      } finally {
        this.isLoading = false
      }
    },
    
    async signOut() {
      this.isLoading = true
      try {
        console.log('开始执行退出登录')
        
        const { error } = await supabase.auth.signOut({})
        if (error) {
          console.error('退出登录请求失败:', error)
        }
        
        this.session = null
        this.user = null
        useTimerStore().$reset()
        
        console.log('退出登录成功')
      } catch (error) {
        console.error('退出登录异常:', error)
        this.session = null
        this.user = null
        useTimerStore().$reset()
      } finally {
        this.isLoading = false
      }
    }
  }
})