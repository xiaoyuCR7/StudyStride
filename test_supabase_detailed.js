// 详细测试 Supabase 认证功能
import { createClient } from '@supabase/supabase-js'

// 使用与前端相同的配置
const url = 'https://juxaojqqosinnvfzfqfo.supabase.co'
const key = 'sb_publishable_iY2f7AQvCZagZi4mfHnw0g_24QWubpr'

const supabase = createClient(url, key)

async function testDetailedRegistration() {
  console.log('=== 详细测试用户注册 ===')
  
  // 生成随机邮箱以避免重复
  const randomEmail = `test_${Date.now()}@example.com`
  const password = 'Test123456'
  
  console.log('测试邮箱:', randomEmail)
  console.log('测试密码:', password)
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email: randomEmail,
      password: password
    })
    
    console.log('完整响应数据:')
    console.log('data:', JSON.stringify(data, null, 2))
    console.log('error:', JSON.stringify(error, null, 2))
    
    if (error) {
      console.error('❌ 注册失败:', error.message)
      console.error('错误代码:', error.code)
      console.error('错误细节:', error.details)
      return false
    }
    
    console.log('✅ 注册成功!')
    return true
  } catch (error) {
    console.error('❌ 注册过程出错:', error)
    return false
  }
}

async function testAuthFlow() {
  console.log('=== 测试完整认证流程 ===')
  
  try {
    // 测试 1: 获取会话
    console.log('\n1. 测试获取会话:')
    const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
    console.log('会话数据:', sessionData)
    console.log('会话错误:', sessionError)
    
    // 测试 2: 获取用户信息
    console.log('\n2. 测试获取用户信息:')
    const { data: userData, error: userError } = await supabase.auth.getUser()
    console.log('用户数据:', userData)
    console.log('用户错误:', userError)
    
    // 测试 3: 尝试注册
    console.log('\n3. 测试用户注册:')
    await testDetailedRegistration()
    
  } catch (error) {
    console.error('❌ 认证流程测试出错:', error)
  }
}

async function testDatabaseAccess() {
  console.log('\n=== 测试数据库访问 ===')
  
  try {
    // 测试访问 study_sessions 表
    console.log('测试访问 study_sessions 表:')
    const { data, error } = await supabase
      .from('study_sessions')
      .select('*')
      .limit(1)
    
    console.log('查询结果:', data)
    console.log('查询错误:', error)
    
  } catch (error) {
    console.error('❌ 数据库访问测试出错:', error)
  }
}

async function runAllTests() {
  console.log('=== Supabase 详细测试 ===')
  
  await testAuthFlow()
  await testDatabaseAccess()
  
  console.log('\n=== 测试完成 ===')
}

runAllTests()
