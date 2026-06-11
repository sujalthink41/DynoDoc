/** Mirrors the backend DTOs (course domain). */

export interface LearnerProfile {
  experience_level: string
  background: string
  goal: string
  weekly_time: string
  notes?: string
}

export interface IntakeSession {
  id: string
  status: 'in_progress' | 'ready'
  goal: string
  questions: string[]
  profile: LearnerProfile | null
}

export interface LectureSummary {
  id: string
  position: number
  title: string
  summary: string
  topics: string[]
  status: string
}

export interface Course {
  id: string
  title: string
  goal: string
  status: string
  lectures: LectureSummary[]
}

export interface CourseSummary {
  id: string
  title: string
  goal: string
  status: string
}

export interface DocView {
  id: string
  position: number
  title: string
  content: string
}

export interface ReferenceView {
  id: string
  type: 'article' | 'youtube'
  url: string
  title: string
}

export interface LectureDetail {
  id: string
  position: number
  title: string
  summary: string
  topics: string[]
  status: string
  docs: DocView[]
  references: ReferenceView[]
}
