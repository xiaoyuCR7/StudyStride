import { supabase } from '../lib/supabase'

export interface SearchResult {
  type: 'post' | 'comment' | 'user'
  id: string
  title?: string
  content: string
  author?: string
  authorId?: string
  createdAt: Date
  relevance?: number
  highlight?: {
    title?: string
    content?: string
  }
}

export interface SearchOptions {
  types?: ('post' | 'comment' | 'user')[]
  sortBy?: 'relevance' | 'date'
  limit?: number
}

function highlightText(text: string, keyword: string): string {
  if (!keyword) return text
  const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

export async function search(query: string, options: SearchOptions = {}): Promise<SearchResult[]> {
  const startTime = performance.now()
  
  const types = options.types || ['post', 'comment', 'user']
  const sortBy = options.sortBy || 'relevance'
  const limit = options.limit || 20
  
  if (!query.trim()) {
    return []
  }
  
  const sanitizedQuery = query.trim().toLowerCase()
  
  const results: SearchResult[] = []
  
  if (types.includes('post')) {
    const { data: posts, error } = await supabase
      .from('community_posts')
      .select('id, title, content, user_name, user_id, created_at')
      .or(`title.ilike.%${sanitizedQuery}%,content.ilike.%${sanitizedQuery}%`)
      .limit(Math.ceil(limit / types.length))
    
    if (!error && posts) {
      posts.forEach(post => {
        const hasTitleMatch = post.title?.toLowerCase().includes(sanitizedQuery)
        const hasContentMatch = post.content.toLowerCase().includes(sanitizedQuery)
        
        const relevance = (hasTitleMatch ? 2 : 0) + (hasContentMatch ? 1 : 0)
        
        results.push({
          type: 'post',
          id: post.id,
          title: post.title,
          content: post.content.slice(0, 100),
          author: post.user_name,
          authorId: post.user_id,
          createdAt: new Date(post.created_at),
          relevance,
          highlight: {
            title: hasTitleMatch ? highlightText(post.title || '', query) : undefined,
            content: hasContentMatch ? highlightText(post.content.slice(0, 100), query) : undefined
          }
        })
      })
    }
  }
  
  if (types.includes('comment')) {
    const { data: comments, error } = await supabase
      .from('community_comments')
      .select('id, content, user_name, user_id, created_at')
      .ilike('content', `%${sanitizedQuery}%`)
      .limit(Math.ceil(limit / types.length))
    
    if (!error && comments) {
      comments.forEach(comment => {
        const hasMatch = comment.content.toLowerCase().includes(sanitizedQuery)
        
        results.push({
          type: 'comment',
          id: comment.id,
          content: comment.content.slice(0, 100),
          author: comment.user_name,
          authorId: comment.user_id,
          createdAt: new Date(comment.created_at),
          relevance: hasMatch ? 1 : 0,
          highlight: {
            content: hasMatch ? highlightText(comment.content.slice(0, 100), query) : undefined
          }
        })
      })
    }
  }
  
  if (types.includes('user')) {
    const { data: users, error } = await supabase
      .from('users')
      .select('id, email')
      .ilike('email', `%${sanitizedQuery}%`)
      .limit(Math.ceil(limit / types.length))
    
    if (!error && users) {
      users.forEach(user => {
        const username = user.email.split('@')[0]
        const hasMatch = user.email.toLowerCase().includes(sanitizedQuery)
        
        results.push({
          type: 'user',
          id: user.id,
          content: username,
          author: username,
          createdAt: new Date(),
          relevance: hasMatch ? 1 : 0,
          highlight: {
            content: hasMatch ? highlightText(username, query) : undefined
          }
        })
      })
    }
  }
  
  if (sortBy === 'relevance') {
    results.sort((a, b) => (b.relevance || 0) - (a.relevance || 0))
  } else {
    results.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
  }
  
  const endTime = performance.now()
  console.log(`[Search] Completed in ${(endTime - startTime).toFixed(2)}ms - ${results.length} results`)
  
  return results.slice(0, limit)
}

export async function searchPosts(query: string, limit: number = 10): Promise<SearchResult[]> {
  const startTime = performance.now()
  
  if (!query.trim()) {
    return []
  }
  
  const sanitizedQuery = query.trim().toLowerCase()
  
  const { data: posts, error } = await supabase
    .from('community_posts')
    .select('id, title, content, user_name, user_id, created_at')
    .or(`title.ilike.%${sanitizedQuery}%,content.ilike.%${sanitizedQuery}%`)
    .order('created_at', { ascending: false })
    .limit(limit)
  
  const endTime = performance.now()
  console.log(`[Search Posts] Completed in ${(endTime - startTime).toFixed(2)}ms`)
  
  if (error || !posts) return []
  
  return posts.map(post => {
    const hasTitleMatch = post.title?.toLowerCase().includes(sanitizedQuery)
    const hasContentMatch = post.content.toLowerCase().includes(sanitizedQuery)
    
    return {
      type: 'post' as const,
      id: post.id,
      title: post.title,
      content: post.content.slice(0, 100),
      author: post.user_name,
      authorId: post.user_id,
      createdAt: new Date(post.created_at),
      highlight: {
        title: hasTitleMatch ? highlightText(post.title || '', query) : undefined,
        content: hasContentMatch ? highlightText(post.content.slice(0, 100), query) : undefined
      }
    }
  })
}