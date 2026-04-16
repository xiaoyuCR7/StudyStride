import { createClient } from '@supabase/supabase-js'

console.log('[StudyStride] 完整 import.meta.env:')
console.log(import.meta.env)

let url = import.meta.env.VITE_SUPABASE_URL ?? ''
let key = import.meta.env.VITE_SUPABASE_ANON_KEY ?? ''

// 硬编码正确的配置（临时解决方案）
if (!url || url.includes('juxaojqqosinnvfzfqfo')) {
  url = 'https://pkhlytcqjgspkmsmzxpg.supabase.co'
}
if (!key || key.includes('iY2f7')) {
  key = 'sb_publishable_ZF3uREWZRRqZpfV-zykABw_W802i9ig'
}

console.log('[StudyStride] 调试信息:')
console.log('- URL:', url)
console.log('- Key:', key ? key.substring(0, 20) + '...' : '未设置')

if (!url || !key) {
  console.warn(
    '[StudyStride] 未配置 VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY，将仅使用本地存储。'
  )
}

export const supabase = createClient(url, key)
