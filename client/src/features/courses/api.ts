import { apiGet, apiPost } from '@/lib/apiClient'
import type { Course, CourseSummary, IntakeSession, LectureDetail } from '@/features/courses/types'

// Intake
export const startIntake = (goal: string) => apiPost<IntakeSession>('/intake', { goal })
export const answerIntake = (id: string, answer: string) =>
  apiPost<IntakeSession>(`/intake/${id}/answer`, { answer })
export const getIntake = (id: string) => apiGet<IntakeSession>(`/intake/${id}`)

// Courses
export const createCourse = (intakeId: string) =>
  apiPost<Course>('/courses', { intake_id: intakeId })
export const listCourses = () => apiGet<CourseSummary[]>('/courses')
export const getCourse = (id: string) => apiGet<Course>(`/courses/${id}`)

// Lectures
export const getLecture = (id: string) => apiGet<LectureDetail>(`/lectures/${id}`)
export const generateTopic = (lectureId: string, topicIndex: number) =>
  apiPost<LectureDetail>(`/lectures/${lectureId}/topics/${topicIndex}`)
export const generateReferences = (lectureId: string) =>
  apiPost<LectureDetail>(`/lectures/${lectureId}/references`)
