import { defineStore } from 'pinia'
import type { Session, User } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { useTimerStore } from './timer'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    session: null as Session | null,
    user: null as User | null
  }),
  getters: {
    isLoggedIn: (s) => !!s.session
  },
  actions: {
    async init() {
      const { data: { session } } = await supabase.auth.getSession()
      this.session = session
      this.user = session?.user ?? null
      await useTimerStore().loadAll()

      supabase.auth.onAuthStateChange(async (event, session) => {
        this.session = session
        this.user = session?.user ?? null
        if (event === 'SIGNED_IN' || event === 'SIGNED_OUT' || event === 'TOKEN_REFRESHED') {
          await useTimerStore().loadAll()
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
      await supabase.auth.signOut()
    }
  }
})
