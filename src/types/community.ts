export interface CommunityPost {
  id: string
  userId: string
  userName: string
  userAvatar?: string
  title: string
  content: string
  type: 'experience' | 'note'
  images: string[]
  createdAt: Date
  updatedAt: Date
  likes: number
  commentsCount: number
  isLiked: boolean
}

export interface CommunityComment {
  id: string
  postId: string
  userId: string
  userName: string
  content: string
  createdAt: Date
}

export interface CommunityLike {
  id: string
  postId: string
  userId: string
  createdAt: Date
}