import { supabase } from '../lib/supabase'
import type { UserProfile, UsernameChange, UsernameValidationResult } from '../types/profile'
import * as communityService from '../services/community'

interface CacheEntry<T> {
  data: T
  timestamp: number
}

const CACHE_TTL = 300000
const PROFILE_CACHE = new Map<string, CacheEntry<UserProfile>>()

const ADJECTIVES = ['快乐的', '聪明的', '勇敢的', '温柔的', '勤奋的', '可爱的', '神秘的', '智慧的', '善良的', '活泼的', '优雅的', '阳光的', '梦幻的', '自由的', '宁静的', '热情的', '冷静的', '浪漫的', '纯真的', '灵动的']
const NOUNS = ['小猫', '小狗', '熊猫', '兔子', '松鼠', '海豚', '蝴蝶', '蜜蜂', '星星', '月亮', '太阳', '云朵', '花朵', '树叶', '小鸟', '鲸鱼', '企鹅', '考拉', '狐狸', '小鹿']

export function generateRandomUsername(): string {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
  const num = Math.floor(Math.random() * 1000)
  return `${adj}${noun}${num}`
}

function getCachedProfile(userId: string): UserProfile | null {
  const entry = PROFILE_CACHE.get(userId)
  if (entry && Date.now() - entry.timestamp < CACHE_TTL) {
    return entry.data
  }
  PROFILE_CACHE.delete(userId)
  return null
}

function setCachedProfile(userId: string, profile: UserProfile): void {
  PROFILE_CACHE.set(userId, { data: profile, timestamp: Date.now() })
}

export function validateUsername(username: string): UsernameValidationResult {
  const errors: string[] = []
  
  if (!username || username.trim() === '') {
    errors.push('用户名不能为空')
    return { valid: false, errors }
  }
  
  const trimmedUsername = username.trim()
  
  const regex = /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/
  if (!regex.test(trimmedUsername)) {
    errors.push('用户名只能包含中文、字母、数字和下划线')
  }
  
  return { valid: errors.length === 0, errors }
}

export async function getUserId(): Promise<string | null> {
  const { data: { user } } = await supabase.auth.getUser()
  return user?.id ?? null
}

export async function getProfile(userId?: string): Promise<UserProfile | null> {
  const targetUserId = userId || await getUserId()
  
  if (!targetUserId) {
    return null
  }
  
  const cached = getCachedProfile(targetUserId)
  if (cached) {
    console.log(`[Profile Cache Hit] User ${targetUserId}`)
    return cached
  }
  
  const { data, error } = await supabase
    .from('user_profiles')
    .select('id, username, avatar_url, created_at, updated_at')
    .eq('id', targetUserId)
    .maybeSingle()
  
  if (error) {
    console.error('[Profile Service] getProfile error:', error)
    throw error
  }
  
  if (!data) {
    return null
  }
  
  const profile: UserProfile = {
    id: data.id,
    username: data.username,
    avatarUrl: data.avatar_url,
    createdAt: new Date(data.created_at),
    updatedAt: new Date(data.updated_at)
  }
  
  setCachedProfile(targetUserId, profile)
  return profile
}

export async function getDisplayUsername(userId?: string): Promise<string> {
  const targetUserId = userId || await getUserId()
  
  if (!targetUserId) {
    return generateRandomUsername()
  }
  
  const profile = await getProfile(targetUserId)
  
  if (profile?.username) {
    return profile.username
  }
  
  const randomUsername = generateRandomUsername()
  
  try {
    await supabase.from('user_profiles').upsert({
      id: targetUserId,
      username: randomUsername,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
    
    PROFILE_CACHE.delete(targetUserId)
  } catch (error) {
    console.error('[Profile Service] Failed to auto-create profile:', error)
  }
  
  return randomUsername
}

export async function getDisplayAvatar(userId?: string): Promise<string | null> {
  const targetUserId = userId || await getUserId()
  
  if (!targetUserId) {
    return null
  }
  
  const profile = await getProfile(targetUserId)
  return profile?.avatarUrl || null
}

export async function updateUsername(newUsername: string): Promise<UserProfile> {
  const userId = await getUserId()
  if (!userId) {
    throw new Error('未登录')
  }
  
  const validation = validateUsername(newUsername)
  if (!validation.valid) {
    throw new Error(validation.errors.join(', '))
  }
  
  const trimmedUsername = newUsername.trim()
  
  const { data: existing, error: checkError } = await supabase
    .from('user_profiles')
    .select('username')
    .eq('id', userId)
    .maybeSingle()
  
  if (checkError) {
    console.error('[Profile Service] updateUsername check error:', checkError)
    throw checkError
  }
  
  const oldUsername = existing?.username || null
  
  if (oldUsername === trimmedUsername) {
    throw new Error('新用户名与当前用户名相同')
  }
  
  const { error: uniqueError } = await supabase
    .from('user_profiles')
    .select('id')
    .eq('username', trimmedUsername)
    .limit(1)
  
  if (uniqueError) {
    console.error('[Profile Service] updateUsername unique check error:', uniqueError)
    throw uniqueError
  }
  
  const { data: updatedProfile, error: updateError } = await supabase
    .from('user_profiles')
    .upsert({
      id: userId,
      username: trimmedUsername,
      updated_at: new Date().toISOString()
    })
    .select()
    .single()
  
  if (updateError) {
    console.error('[Profile Service] updateUsername error:', updateError)
    throw updateError
  }
  
  await supabase.from('username_history').insert({
    user_id: userId,
    old_username: oldUsername,
    new_username: trimmedUsername,
    changed_at: new Date().toISOString()
  })
  
  try {
    await communityService.syncUsernameToPosts(userId, trimmedUsername)
    console.log('[Profile Service] Username synced to posts successfully')
  } catch (syncError) {
    console.error('[Profile Service] Failed to sync username to posts:', syncError)
  }
  
  PROFILE_CACHE.delete(userId)
  
  const profile: UserProfile = {
    id: updatedProfile.id,
    username: updatedProfile.username,
    avatarUrl: updatedProfile.avatar_url,
    createdAt: new Date(updatedProfile.created_at),
    updatedAt: new Date(updatedProfile.updated_at)
  }
  
  return profile
}

export async function updateAvatar(file: File): Promise<UserProfile> {
  const userId = await getUserId()
  if (!userId) {
    throw new Error('未登录')
  }
  
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('不支持的文件格式，仅支持 JPG、PNG、GIF')
  }
  
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('文件大小超过限制，最大支持5MB')
  }
  
  const fileName = `avatars/${userId}_${Date.now()}.${file.type.split('/')[1]}`
  
  const { error: uploadError } = await supabase.storage
    .from('avatars')
    .upload(fileName, file, {
      cacheControl: '3600',
      upsert: true
    })
  
  if (uploadError) {
    console.error('[Profile Service] updateAvatar upload error:', uploadError)
    throw uploadError
  }
  
  const { data: urlData } = supabase.storage
    .from('avatars')
    .getPublicUrl(fileName)
  
  const { data: updatedProfile, error: updateError } = await supabase
    .from('user_profiles')
    .upsert({
      id: userId,
      avatar_url: urlData.publicUrl,
      updated_at: new Date().toISOString()
    })
    .select()
    .single()
  
  if (updateError) {
    console.error('[Profile Service] updateAvatar update error:', updateError)
    throw updateError
  }
  
  try {
    await communityService.syncAvatarToPosts(userId, urlData.publicUrl)
    console.log('[Profile Service] Avatar synced to posts successfully')
  } catch (syncError) {
    console.error('[Profile Service] Failed to sync avatar to posts:', syncError)
  }
  
  PROFILE_CACHE.delete(userId)
  
  const profile: UserProfile = {
    id: updatedProfile.id,
    username: updatedProfile.username,
    avatarUrl: updatedProfile.avatar_url,
    createdAt: new Date(updatedProfile.created_at),
    updatedAt: new Date(updatedProfile.updated_at)
  }
  
  return profile
}

export async function getUsernameHistory(userId?: string): Promise<UsernameChange[]> {
  const targetUserId = userId || await getUserId()
  
  if (!targetUserId) {
    return []
  }
  
  const { data, error } = await supabase
    .from('username_history')
    .select('id, user_id, old_username, new_username, changed_at')
    .eq('user_id', targetUserId)
    .order('changed_at', { ascending: false })
  
  if (error) {
    console.error('[Profile Service] getUsernameHistory error:', error)
    throw error
  }
  
  return (data || []).map(row => ({
    id: row.id,
    userId: row.user_id,
    oldUsername: row.old_username,
    newUsername: row.new_username,
    changedAt: new Date(row.changed_at)
  }))
}

export async function deleteAvatar(): Promise<UserProfile> {
  const userId = await getUserId()
  if (!userId) {
    throw new Error('未登录')
  }
  
  const { data: profile, error: getError } = await supabase
    .from('user_profiles')
    .select('avatar_url')
    .eq('id', userId)
    .maybeSingle()
  
  if (getError) {
    console.error('[Profile Service] deleteAvatar get error:', getError)
    throw getError
  }
  
  if (profile?.avatar_url) {
    const fileName = profile.avatar_url.split('/').pop()
    if (fileName) {
      await supabase.storage.from('avatars').remove([fileName])
    }
  }
  
  const { data: updatedProfile, error: updateError } = await supabase
    .from('user_profiles')
    .update({
      avatar_url: null,
      updated_at: new Date().toISOString()
    })
    .eq('id', userId)
    .select()
    .single()
  
  if (updateError) {
    console.error('[Profile Service] deleteAvatar update error:', updateError)
    throw updateError
  }
  
  PROFILE_CACHE.delete(userId)
  
  return {
    id: updatedProfile.id,
    username: updatedProfile.username,
    avatarUrl: updatedProfile.avatar_url,
    createdAt: new Date(updatedProfile.created_at),
    updatedAt: new Date(updatedProfile.updated_at)
  }
}

export function clearProfileCache(userId?: string): void {
  if (userId) {
    PROFILE_CACHE.delete(userId)
  } else {
    PROFILE_CACHE.clear()
  }
}