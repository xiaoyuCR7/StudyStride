export interface StudySession {
  id: string
  startTime: Date
  endTime: Date | null
  duration: number
  content: string
  date: string
  subject: string
}

export interface Subject {
  id: string
  name: string
}
