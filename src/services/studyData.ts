import { supabase } from '../lib/supabase'
import type { StudySession, Subject } from '../types/study'

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function ensureUuid(id: string): string {
  return UUID_RE.test(id) ? id : crypto.randomUUID()
}

function normalizeDate(d: Date | string): Date {
  return d instanceof Date ? d : new Date(d)
}

export function normalizeSession(raw: Record<string, unknown>): StudySession {
  return {
    id: String(raw.id),
    startTime: normalizeDate(raw.startTime as Date | string),
    endTime: raw.endTime ? normalizeDate(raw.endTime as Date | string) : null,
    duration: Number(raw.duration),
    content: String(raw.content ?? ''),
    date: String(raw.date),
    subject: String(raw.subject ?? '未分类')
  }
}

export async function getRemoteSession(): Promise<boolean> {
  const { data } = await supabase.auth.getSession()
  return !!data.session
}

async function getUserId(): Promise<string | null> {
  const { data: { user } } = await supabase.auth.getUser()
  return user?.id ?? null
}

type SessionRow = {
  id: string
  user_id: string
  subject: string
  content: string
  duration: number
  start_time: string
  end_time: string | null
  session_date: string
}

function rowToSession(row: SessionRow): StudySession {
  const d = row.session_date
  const dateStr = d.includes('T') ? d.split('T')[0]! : d
  return {
    id: row.id,
    startTime: new Date(row.start_time),
    endTime: row.end_time ? new Date(row.end_time) : null,
    duration: row.duration,
    content: row.content ?? '',
    date: dateStr,
    subject: row.subject
  }
}

function sessionToRow(s: StudySession, userId: string): SessionRow {
  return {
    id: ensureUuid(s.id),
    user_id: userId,
    subject: s.subject,
    content: s.content,
    duration: s.duration,
    start_time: normalizeDate(s.startTime).toISOString(),
    end_time: s.endTime ? normalizeDate(s.endTime).toISOString() : null,
    session_date: s.date
  }
}

export async function fetchSessions(): Promise<StudySession[]> {
  const { data, error } = await supabase
    .from('study_sessions')
    .select('*')
    .order('start_time', { ascending: false })
  if (error) throw error
  return (data as SessionRow[]).map(rowToSession)
}

export async function replaceAllSessions(sessions: StudySession[]): Promise<StudySession[]> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const { error: delErr } = await supabase
    .from('study_sessions')
    .delete()
    .eq('user_id', userId)
  if (delErr) throw delErr

  const out: StudySession[] = []
  for (const s of sessions) {
    const id = ensureUuid(s.id)
    const row = sessionToRow({ ...s, id }, userId)
    const { error } = await supabase.from('study_sessions').insert(row)
    if (error) throw error
    out.push({
      ...s,
      id,
      startTime: normalizeDate(s.startTime),
      endTime: s.endTime ? normalizeDate(s.endTime) : null
    })
  }
  return out
}

type SubjectRow = {
  id: string
  user_id: string
  name: string
  created_at: string
}

export async function fetchSubjects(): Promise<Subject[]> {
  const { data, error } = await supabase
    .from('subjects')
    .select('*')
    .order('created_at', { ascending: true })
  if (error) throw error
  return (data as SubjectRow[]).map((r) => ({ id: r.id, name: r.name }))
}

export async function replaceAllSubjects(subjects: Subject[]): Promise<Subject[]> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')

  const { error: delErr } = await supabase.from('subjects').delete().eq('user_id', userId)
  if (delErr) throw delErr

  const out: Subject[] = []
  for (const sub of subjects) {
    const id = ensureUuid(sub.id)
    const { error } = await supabase.from('subjects').insert({
      id,
      user_id: userId,
      name: sub.name
    })
    if (error) throw error
    out.push({ id, name: sub.name })
  }
  return out
}

export async function fetchUserSettings(): Promise<{ reminder_interval: number } | null> {
  const userId = await getUserId()
  if (!userId) return null
  const { data, error } = await supabase
    .from('user_settings')
    .select('reminder_interval')
    .eq('user_id', userId)
    .maybeSingle()
  if (error) throw error
  if (!data) return null
  return { reminder_interval: data.reminder_interval as number }
}

export async function upsertUserSettings(reminderInterval: number): Promise<void> {
  const userId = await getUserId()
  if (!userId) throw new Error('未登录')
  const { error } = await supabase.from('user_settings').upsert(
    { user_id: userId, reminder_interval: reminderInterval },
    { onConflict: 'user_id' }
  )
  if (error) throw error
}
