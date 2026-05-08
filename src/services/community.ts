import { supabase } from '../lib/supabase'
import type { CommunityPost, CommunityComment } from '../types/community'
import * as profileService from '../services/profile'

interface CacheEntry<T> {
  data: T
  timestamp: number
}

const CACHE_TTL = 60000
const POSTS_CACHE = new Map<string, CacheEntry<CommunityPost[]>>()
const POST_CACHE = new Map<string, CacheEntry<CommunityPost>>()
const POPULAR_POSTS_CACHE = new Map<string, CacheEntry<CommunityPost[]>>()

function getCachedData<T>(cache: Map<string, CacheEntry<T>>, key: string): T | null {
  const entry = cache.get(key)
  if (entry && Date.now() - entry.timestamp < CACHE_TTL) {
    return entry.data
  }
  cache.delete(key)
  return null
}

function setCachedData<T>(cache: Map<string, CacheEntry<T>>, key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() })
}

async function getUserId(): Promise<string | null> {
  const { data: { user } } = await supabase.auth.getUser()
  return user?.id ?? null
}

type PostRow = {
  id: string
  user_id: string
  user_name: string
  user_avatar?: string
  title: string
  content: string
  type: 'experience' | 'note'
  images: string[]
  created_at: string
  updated_at: string
  likes_count: number
  comments_count: number
}

function rowToPost(row: PostRow, isLiked: boolean): CommunityPost {
  return {
    id: row.id,
    userId: row.user_id,
    userName: row.user_name,
    userAvatar: row.user_avatar,
    title: row.title,
    content: row.content,
    type: row.type,
    images: row.images || [],
    createdAt: new Date(row.created_at),
    updatedAt: new Date(row.updated_at),
    likes: row.likes_count,
    commentsCount: row.comments_count,
    isLiked
  }
}

export async function fetchPosts(page: number = 1, pageSize: number = 20, type?: 'experience' | 'note'): Promise<CommunityPost[]> {
  const userId = await getUserId()
  const cacheKey = `${type || 'all'}_page_${page}_size_${pageSize}`
  
  const cached = getCachedData(POSTS_CACHE, cacheKey)
  if (cached) {
    console.log(`[Cache Hit] fetchPosts ${cacheKey}`)
    return cached
  }

  const offset = (page - 1) * pageSize
  const startTime = performance.now()

  let query = supabase
    .from('community_posts')
    .select('id, user_id, user_name, user_avatar, title, content, type, images, created_at, updated_at, likes_count, comments_count')
    .order('created_at', { ascending: false })
    .range(offset, offset + pageSize - 1)

  if (type) {
    query = query.eq('type', type)
  }

  const { data, error } = await query
  
  const queryTime = performance.now() - startTime
  
  if (error) {
    console.error('[Community Service] fetchPosts query error:', error)
    throw error
  }

  if (!data || data.length === 0) {
    setCachedData(POSTS_CACHE, cacheKey, [])
    return []
  }

  const postIds = (data as PostRow[]).map(p => p.id)
  
  const likesStartTime = performance.now()
  
  const { data: likeData, error: likeError } = await supabase
    .from('community_likes')
    .select('post_id')
    .in('post_id', postIds)
    .eq('user_id', userId || '')
  
  const likesTime = performance.now() - likesStartTime

  if (likeError) {
    console.error('[Community Service] fetchPosts likes query error:', likeError)
    throw likeError
  }

  const likedIds = new Set((likeData || []).map(l => l.post_id))
  const result = (data as PostRow[]).map(row => rowToPost(row, likedIds.has(row.id)))

  setCachedData(POSTS_CACHE, cacheKey, result)
  
  console.log(`[Performance] fetchPosts completed in ${(queryTime + likesTime).toFixed(2)}ms (query: ${queryTime.toFixed(2)}ms, likes: ${likesTime.toFixed(2)}ms) - ${result.length} posts`)

  return result
}

export async function fetchPostById(id: string): Promise<CommunityPost | null> {
  const userId = await getUserId()
  
  const cached = getCachedData(POST_CACHE, id)
  if (cached) {
    console.log(`[Cache Hit] fetchPostById ${id}`)
    return cached
  }
  
  const { data, error } = await supabase
    .from('community_posts')
    .select('id, user_id, user_name, user_avatar, title, content, type, images, created_at, updated_at, likes_count, comments_count')
    .eq('id', id)
    .maybeSingle()

  if (error) {
    console.error('[Community Service] fetchPostById error:', error)
    throw error
  }
  if (!data) return null

  const { data: likeData, error: likeError } = await supabase
    .from('community_likes')
    .select('post_id')
    .eq('post_id', id)
    .eq('user_id', userId || '')

  if (likeError) {
    console.error('[Community Service] fetchPostById likes error:', likeError)
    throw likeError
  }

  const result = rowToPost(data as PostRow, !!likeData && likeData.length > 0)
  setCachedData(POST_CACHE, id, result)
  
  return result
}

export async function createPost(post: {
  title: string
  content: string
  type: 'experience' | 'note'
  images?: string[]
}): Promise<CommunityPost> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const userName = await profileService.getDisplayUsername(userId)

  const { data, error } = await supabase
    .from('community_posts')
    .insert({
      user_id: userId,
      user_name: userName,
      title: post.title,
      content: post.content,
      type: post.type,
      images: post.images || [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      likes_count: 0,
      comments_count: 0
    })
    .select()
    .single()

  if (error) {
    console.error('[Community Service] createPost error:', error)
    throw error
  }

  POSTS_CACHE.clear()
  
  return rowToPost(data as PostRow, false)
}

export async function syncUsernameToPosts(userId: string, newUsername: string): Promise<void> {
  const { error } = await supabase
    .from('community_posts')
    .update({ user_name: newUsername })
    .eq('user_id', userId)
  
  if (error) {
    console.error('[Community Service] syncUsernameToPosts error:', error)
    throw error
  }
  
  POSTS_CACHE.clear()
  POST_CACHE.clear()
}

export async function syncAvatarToPosts(userId: string, newAvatarUrl: string): Promise<void> {
  const { error } = await supabase
    .from('community_posts')
    .update({ user_avatar: newAvatarUrl })
    .eq('user_id', userId)
  
  if (error) {
    console.error('[Community Service] syncAvatarToPosts error:', error)
    throw error
  }
  
  POSTS_CACHE.clear()
  POST_CACHE.clear()
}

export async function updatePost(id: string, updates: {
  title?: string
  content?: string
  images?: string[]
}): Promise<CommunityPost | null> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const { data: existing, error: getError } = await supabase
    .from('community_posts')
    .select('user_id')
    .eq('id', id)
    .maybeSingle()

  if (getError) {
    console.error('[Community Service] updatePost get existing error:', getError)
    throw getError
  }
  if (!existing || existing.user_id !== userId) {
    throw new Error('无权修改此帖子')
  }

  const { data, error } = await supabase
    .from('community_posts')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', id)
    .select()
    .single()

  if (error) {
    console.error('[Community Service] updatePost error:', error)
    throw error
  }
  if (!data) return null

  POSTS_CACHE.clear()
  POST_CACHE.delete(id)

  return rowToPost(data as PostRow, false)
}

export async function deletePost(id: string): Promise<void> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const { data: existing, error: getError } = await supabase
    .from('community_posts')
    .select('user_id')
    .eq('id', id)
    .maybeSingle()

  if (getError) {
    console.error('[Community Service] deletePost get existing error:', getError)
    throw getError
  }
  if (!existing || existing.user_id !== userId) {
    throw new Error('无权删除此帖子')
  }

  const { error } = await supabase.from('community_posts').delete().eq('id', id)
  if (error) {
    console.error('[Community Service] deletePost error:', error)
    throw error
  }

  POSTS_CACHE.clear()
  POST_CACHE.delete(id)
}

export async function toggleLike(postId: string): Promise<{ liked: boolean; count: number }> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  try {
    const { data: existing, error: getError } = await supabase
      .from('community_likes')
      .select('id')
      .eq('post_id', postId)
      .eq('user_id', userId)
      .maybeSingle()

    if (getError) {
      console.error('[Community Service] toggleLike check existing error:', getError)
      throw getError
    }

    if (existing) {
      const { error: deleteError } = await supabase.from('community_likes').delete().eq('id', existing.id)
      if (deleteError) {
        console.error('[Community Service] toggleLike delete error:', deleteError)
        throw deleteError
      }

      const { error: rpcError } = await supabase.rpc('decrement_likes', { post_id: postId })
      if (rpcError) {
        console.error('[Community Service] toggleLike decrement_likes error:', rpcError)
        throw rpcError
      }
    } else {
      const { error: insertError } = await supabase.from('community_likes').insert({
        post_id: postId,
        user_id: userId,
        created_at: new Date().toISOString()
      })
      if (insertError) {
        console.error('[Community Service] toggleLike insert error:', insertError)
        throw insertError
      }

      const { error: rpcError } = await supabase.rpc('increment_likes', { post_id: postId })
      if (rpcError) {
        console.error('[Community Service] toggleLike increment_likes error:', rpcError)
        throw rpcError
      }
    }

    const { data: countData, error: countError } = await supabase
      .from('community_posts')
      .select('likes_count')
      .eq('id', postId)
      .single()

    if (countError) {
      console.error('[Community Service] toggleLike get count error:', countError)
      throw countError
    }

    POST_CACHE.delete(postId)

    return { 
      liked: !existing, 
      count: (countData as { likes_count: number }).likes_count 
    }

  } catch (error) {
    console.error('[Community Service] toggleLike failed:', error)
    throw error
  }
}

type CommentRow = {
  id: string
  post_id: string
  user_id: string
  user_name: string
  content: string
  created_at: string
}

function rowToComment(row: CommentRow): CommunityComment {
  return {
    id: row.id,
    postId: row.post_id,
    userId: row.user_id,
    userName: row.user_name,
    content: row.content,
    createdAt: new Date(row.created_at)
  }
}

export async function fetchComments(postId: string): Promise<CommunityComment[]> {
  const { data, error } = await supabase
    .from('community_comments')
    .select('id, post_id, user_id, user_name, content, created_at')
    .eq('post_id', postId)
    .order('created_at', { ascending: true })

  if (error) {
    console.error('[Community Service] fetchComments error:', error)
    throw error
  }
  return (data as CommentRow[]).map(rowToComment)
}

export async function createComment(postId: string, content: string): Promise<CommunityComment> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const user = await supabase.auth.getUser()
  const userName = user.data.user?.email?.split('@')[0] || '用户'

  try {
    const { data, error } = await supabase
      .from('community_comments')
      .insert({
        post_id: postId,
        user_id: userId,
        user_name: userName,
        content,
        created_at: new Date().toISOString()
      })
      .select()
      .single()

    if (error) {
      console.error('[Community Service] createComment insert error:', error)
      throw error
    }

    const { error: rpcError } = await supabase.rpc('increment_comments', { post_id: postId })
    if (rpcError) {
      console.error('[Community Service] createComment increment_comments error:', rpcError)
      throw rpcError
    }

    POST_CACHE.delete(postId)

    return rowToComment(data as CommentRow)

  } catch (error) {
    console.error('[Community Service] createComment failed:', error)
    throw error
  }
}

export async function deleteComment(id: string): Promise<void> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  try {
    const { data: existing, error: getError } = await supabase
      .from('community_comments')
      .select('user_id, post_id')
      .eq('id', id)
      .maybeSingle()

    if (getError) {
      console.error('[Community Service] deleteComment get existing error:', getError)
      throw getError
    }
    if (!existing || existing.user_id !== userId) {
      throw new Error('无权删除此评论')
    }

    const { error: deleteError } = await supabase.from('community_comments').delete().eq('id', id)
    if (deleteError) {
      console.error('[Community Service] deleteComment delete error:', deleteError)
      throw deleteError
    }

    const { error: rpcError } = await supabase.rpc('decrement_comments', { post_id: existing.post_id })
    if (rpcError) {
      console.error('[Community Service] deleteComment decrement_comments error:', rpcError)
      throw rpcError
    }

    POST_CACHE.delete(existing.post_id)

  } catch (error) {
    console.error('[Community Service] deleteComment failed:', error)
    throw error
  }
}

export async function fetchPopularPosts(limit: number = 5): Promise<CommunityPost[]> {
  const userId = await getUserId()
  const cacheKey = `popular_${limit}`
  
  const cached = getCachedData(POPULAR_POSTS_CACHE, cacheKey)
  if (cached) {
    console.log(`[Cache Hit] fetchPopularPosts ${cacheKey}`)
    return cached
  }

  const { data, error } = await supabase
    .from('community_posts')
    .select('id, user_id, user_name, title, content, type, images, created_at, updated_at, likes_count, comments_count')
    .order('likes_count', { ascending: false })
    .limit(limit)

  if (error) {
    console.error('[Community Service] fetchPopularPosts error:', error)
    throw error
  }

  if (!data || data.length === 0) {
    setCachedData(POPULAR_POSTS_CACHE, cacheKey, [])
    return []
  }

  const postIds = (data as PostRow[]).map(p => p.id)
  
  const { data: likeData } = await supabase
    .from('community_likes')
    .select('post_id')
    .in('post_id', postIds)
    .eq('user_id', userId || '')

  const likedIds = new Set((likeData || []).map(l => l.post_id))
  const result = (data as PostRow[]).map(row => rowToPost(row, likedIds.has(row.id)))

  setCachedData(POPULAR_POSTS_CACHE, cacheKey, result)
  
  return result
}

export function clearCache(): void {
  POSTS_CACHE.clear()
  POST_CACHE.clear()
  POPULAR_POSTS_CACHE.clear()
  console.log('[Cache] All caches cleared')
}