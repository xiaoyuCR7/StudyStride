// 直接测试 Supabase API 注册端点
import { createClient } from '@supabase/supabase-js'

// 配置信息
const config = {
  url: 'https://juxaojqqosinnvfzfqfo.supabase.co',
  anonKey: 'sb_publishable_iY2f7AQvCZagZi4mfHnw0g_24QWubpr'
}

console.log('=== 直接测试 Supabase API ===')
console.log('API URL:', config.url)

// 测试 1: 直接调用注册 API
async function testDirectSignUp() {
  console.log('\n=== 测试直接调用注册 API ===')
  
  const email = `test_api_${Date.now()}@example.com`
  const password = 'Test123456'
  
  console.log('测试邮箱:', email)
  
  const headers = {
    'apikey': config.anonKey,
    'Content-Type': 'application/json'
  }
  
  try {
    const response = await fetch(`${config.url}/auth/v1/signup`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        email: email,
        password: password
      })
    })
    
    console.log('响应状态码:', response.status)
    console.log('响应状态文本:', response.statusText)
    
    const responseData = await response.json()
    console.log('响应数据:', JSON.stringify(responseData, null, 2))
    
    if (response.ok) {
      console.log('✅ 注册成功!')
    } else {
      console.log('❌ 注册失败!')
    }
    
  } catch (error) {
    console.error('❌ API 调用失败:', error.message)
  }
}

// 测试 2: 测试登录 API
async function testDirectSignIn() {
  console.log('\n=== 测试直接调用登录 API ===')
  
  const email = `test_api_${Date.now() - 10000}@example.com`
  const password = 'Test123456'
  
  console.log('测试邮箱:', email)
  
  const headers = {
    'apikey': config.anonKey,
    'Content-Type': 'application/json'
  }
  
  try {
    const response = await fetch(`${config.url}/auth/v1/token?grant_type=password`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        email: email,
        password: password
      })
    })
    
    console.log('响应状态码:', response.status)
    console.log('响应状态文本:', response.statusText)
    
    const responseData = await response.json()
    console.log('响应数据:', JSON.stringify(responseData, null, 2))
    
    if (response.ok) {
      console.log('✅ 登录成功!')
    } else {
      console.log('❌ 登录失败!')
    }
    
  } catch (error) {
    console.error('❌ API 调用失败:', error.message)
  }
}

// 测试 3: 测试会话 API
async function testSession() {
  console.log('\n=== 测试会话 API ===')
  
  const headers = {
    'apikey': config.anonKey
  }
  
  try {
    const response = await fetch(`${config.url}/auth/v1/session`, {
      method: 'GET',
      headers: headers
    })
    
    console.log('响应状态码:', response.status)
    console.log('响应状态文本:', response.statusText)
    
    const responseData = await response.json()
    console.log('响应数据:', JSON.stringify(responseData, null, 2))
    
  } catch (error) {
    console.error('❌ 会话 API 调用失败:', error.message)
  }
}

// 测试 4: 测试使用 supabase-js 客户端
async function testSupabaseClient() {
  console.log('\n=== 测试使用 supabase-js 客户端 ===')
  
  const supabase = createClient(config.url, config.anonKey)
  
  const email = `test_client_${Date.now()}@example.com`
  const password = 'Test123456'
  
  console.log('测试邮箱:', email)
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email: email,
      password: password
    })
    
    console.log('客户端响应 - data:', JSON.stringify(data, null, 2))
    console.log('客户端响应 - error:', JSON.stringify(error, null, 2))
    
    if (error) {
      console.log('❌ 客户端注册失败:', error.message)
      console.log('错误代码:', error.code)
      console.log('错误状态:', error.status)
    } else {
      console.log('✅ 客户端注册成功!')
    }
    
  } catch (error) {
    console.error('❌ 客户端调用失败:', error.message)
  }
}

async function runAllTests() {
  console.log('=== 开始测试 Supabase API ===')
  
  await testDirectSignUp()
  await testDirectSignIn()
  await testSession()
  await testSupabaseClient()
  
  console.log('\n=== 测试完成 ===')
}

runAllTests()
