// 测试 Supabase 认证功能
import { createClient } from '@supabase/supabase-js'

// 使用与前端相同的配置
const url = 'https://juxaojqqosinnvfzfqfo.supabase.co'
const key = 'sb_publishable_iY2f7AQvCZagZi4mfHnw0g_24QWubpr'

const supabase = createClient(url, key)

async function testSupabaseConnection() {
  console.log('测试 Supabase 连接...')
  
  try {
    // 测试获取会话
    const { data: { session } } = await supabase.auth.getSession()
    console.log('当前会话:', session ? '已登录' : '未登录')
    
    // 测试用户信息
    const { data: { user } } = await supabase.auth.getUser()
    console.log('当前用户:', user ? user.email : '无用户')
    
    console.log('✅ Supabase 连接正常')
    return true
  } catch (error) {
    console.error('❌ Supabase 连接失败:', error.message)
    return false
  }
}

async function testUserRegistration() {
  console.log('测试用户注册...')
  
  // 生成随机邮箱以避免重复
  const randomEmail = `test_${Date.now()}@example.com`
  const password = 'Test123456'
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email: randomEmail,
      password: password
    })
    
    if (error) {
      console.error('❌ 注册失败:', error.message)
      return false
    }
    
    console.log('✅ 注册成功!')
    console.log('用户 ID:', data.user?.id)
    console.log('邮箱:', data.user?.email)
    console.log('需要邮箱验证:', data.user?.email_confirmed_at ? '否' : '是')
    
    return true
  } catch (error) {
    console.error('❌ 注册过程出错:', error.message)
    return false
  }
}

async function testUserLogin() {
  console.log('测试用户登录...')
  
  // 使用刚才注册的邮箱登录
  const randomEmail = `test_${Date.now() - 10000}@example.com`
  const password = 'Test123456'
  
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: randomEmail,
      password: password
    })
    
    if (error) {
      console.error('❌ 登录失败:', error.message)
      return false
    }
    
    console.log('✅ 登录成功!')
    console.log('用户 ID:', data.user?.id)
    console.log('邮箱:', data.user?.email)
    
    return true
  } catch (error) {
    console.error('❌ 登录过程出错:', error.message)
    return false
  }
}

async function runAllTests() {
  console.log('=== Supabase 认证测试 ===')
  
  const connectionTest = await testSupabaseConnection()
  if (!connectionTest) {
    console.log('连接测试失败，停止后续测试')
    return
  }
  
  await testUserRegistration()
  await testUserLogin()
  
  console.log('=== 测试完成 ===')
}

runAllTests()
