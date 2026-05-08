export interface UserProfile {
  id: string
  username: string | null
  avatarUrl: string | null
  createdAt: Date
  updatedAt: Date
}

export interface UsernameChange {
  id: string
  userId: string
  oldUsername: string | null
  newUsername: string
  changedAt: Date
}

export interface ProfileUpdate {
  username?: string
  avatar?: File
}

export interface UsernameValidationResult {
  valid: boolean
  errors: string[]
}