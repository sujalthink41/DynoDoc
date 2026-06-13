/** Mirrors the backend DTOs (course domain). */

export interface LearnerProfile {
  experience_level: string
  background: string
  goal: string
  weekly_time: string
  notes?: string
}

export interface TranscriptTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface IntakeSession {
  id: string
  status: 'in_progress' | 'ready'
  goal: string
  transcript: TranscriptTurn[]
  profile: LearnerProfile | null
}

export interface IntakeSummary {
  id: string
  goal: string
  status: string
  created_at: string
}

export interface LectureSummary {
  id: string
  position: number
  title: string
  summary: string
  topics: string[]
  status: string
  lessons_total: number
  lessons_passed: number
}

export interface Course {
  id: string
  title: string
  goal: string
  status: string
  completion_percent: number
  average_score: number
  lectures: LectureSummary[]
}

export interface CourseSummary {
  id: string
  title: string
  goal: string
  status: string
  completion_percent: number
  average_score: number
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

export interface LessonState {
  index: number
  topic: string
  generated: boolean
  unlocked: boolean
  attempted: boolean
  passed: boolean
  mastered: boolean
  score: number
}

export interface LectureDetail {
  id: string
  position: number
  title: string
  summary: string
  status: string
  course_id: string
  course_title: string
  lessons: LessonState[]
  docs: DocView[]
  references: ReferenceView[]
}

export interface QuizQuestionView {
  question: string
  options: string[]
}

export interface QuizView {
  lecture_id: string
  topic_index: number
  questions: QuizQuestionView[]
  best_score: number
  mastered: boolean
  /** Correct option per question — present only in mastered review mode. */
  answers: number[] | null
}

export interface QuizResultItem {
  correct: boolean
  /** Correct option — revealed only once the lesson is mastered (100%). */
  answer_index: number | null
}

export interface QuizResult {
  score: number
  passed: boolean
  total: number
  correct_count: number
  mastered: boolean
  can_retake: boolean
  results: QuizResultItem[]
  unlocked_next: boolean
}
