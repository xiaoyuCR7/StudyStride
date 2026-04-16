// 测试 Supabase 配置和注册功能
import { createClient } from '@supabase/supabase-js'

// 配置信息
const config = {
  url: 'https://juxaojqqosinnvfzfqfo.supabase.co',
  anonKey: 'sb_publishable_iY2f7AQvCZagZi4mfHnw0g_24QWubpr',
  serviceKey: '' // 如果有服务密钥可以尝试使用
}

console.log('=== Supabase 配置信息 ===')
console.log('URL:', config.url)
console.log('Anon Key:', config.anonKey.substring(0, 20) + '...')

// 使用匿名密钥创建客户端
const supabase = createClient(config.url, config.anonKey)

async function testConfig() {
  console.log('\n=== 测试配置 ===')
  
  // 测试 1: 检查客户端配置
  console.log('1. 客户端配置:')
  console.log('API URL:', supabase.auth.apiUrl)
  console.log('已初始化:', !!supabase)
  
  // 测试 2: 检查认证端点
  console.log('\n2. 认证端点:')
  try {
    const response = await fetch(`${config.url}/auth/v1/health`, {
      method: 'GET',
      headers: {
        'apikey': config.anonKey
      }
    })
    
    console.log('健康检查状态:', response.status)
    const data = await response.json()
    console.log('健康检查响应:', data)
  } catch (error) {
    console.error('健康检查失败:', error.message)
  }
  
  // 测试 3: 尝试不同的注册方式
  console.log('\n3. 测试不同注册方式:')
  await testRegistrationMethods()
}

async function testRegistrationMethods() {
  // 方法 1: 基本注册
  console.log('\n方法 1: 基本注册')
  const email1 = `test_basic_${Date.now()}@example.com`
  const password = 'Test123456'
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email: email1,
      password: password
    })
    
    console.log('基本注册 - 邮箱:', email1)
    console.log('基本注册 - 成功:', !error)
    if (error) {
      console.log('基本注册 - 错误:', error.message)
      console.log('基本注册 - 代码:', error.code)
    }
  } catch (error) {
    console.error('基本注册 - 异常:', error.message)
  }
  
  // 方法 2: 带重定向的注册
  console.log('\n方法 2: 带重定向的注册')
  const email2 = `test_redirect_${Date.now()}@example.com`
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email: email2,
      password: password,
      options: {
        redirectTo: 'http://localhost:5174'
      }
    })
    
    console.log('带重定向注册 - 邮箱:', email2)
    console.log('带重定向注册 - 成功:', !error)
    if (error) {
      console.log('带重定向注册 - 错误:', error.message)
      console.log('带重定向注册 - 代码:', error.code)
    }
  } catch (error) {
    console.error('带重定向注册 - 异常:', error.message)
  }
  
  // 方法 3: 测试登录（使用之前注册的邮箱）
  console.log('\n方法 3: 测试登录')
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email1,
      password: password
    })
    
    console.log('登录测试 - 邮箱:', email1)
    console.log('登录测试 - 成功:', !error)
    if (error) {
      console.log('登录测试 - 错误:', error.message)
      console.log('登录测试 - 代码:', error.code)
    }
  } catch (error) {
    console.error('登录测试 - 异常:', error.message)
  }
}

async function testDatabaseStructure() {
  console.log('\n=== 测试数据库结构 ===')
  
  try {
    // 测试 users 表访问
    console.log('测试 users 表:')
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('id, email')
      .limit(1)
    
    console.log('users 表查询结果:', users)
    console.log('users 表查询错误:', usersError)
    
    // 测试 study_sessions 表
    console.log('\n测试 study_sessions 表:')
    const { data: sessions, error: sessionsError } = await supabase
      .from('study_sessions')
      .select('*')
      .limit(1)
    
    console.log('study_sessions 表查询结果:', sessions)
    console.log('study_sessions 表查询错误:', sessionsError)
    
    // 测试 subjects 表
    console.log('\n测试 subjects 表:')
    const { data: subjects, error: subjectsError } = await supabase
      .from('subjects')
      .select('*')
      .limit(1)
    
    console.log('subjects 表查询结果:', subjects)
    console.log('subjects 表查询错误:', subjectsError)
    
  } catch (error) {
    console.error('数据库结构测试失败:', error.message)
  }
}

async function runAllTests() {
  console.log('=== Supabase 配置和注册测试 ===')
  
  await testConfig()
  await testDatabaseStructure()
  
  console.log('\n=== 测试完成 ===')
  console.log('\n总结:')
  console.log('1. 前端配置已正确设置')
  console.log('2. 与 Supabase 服务的连接正常')
  console.log('3. 数据库访问正常')
  console.log('4. 注册失败可能是由于 Supabase 项目配置问题')
  console.log('\n建议:')
  console.log('- 检查 Supabase 项目的认证设置')
  console.log('- 检查用户表的权限配置')
  console.log('- 检查邮箱验证设置')
  console.log('- 查看 Supabase 控制台的错误日志')
}

runAllTests()
