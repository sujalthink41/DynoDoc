import { apiGet, apiPost } from '@/lib/apiClient'
import type {
  Course,
  CourseSummary,
  IntakeSession,
  IntakeSummary,
  LectureDetail,
  QuizResult,
  QuizView,
  TutorReply,
  TutorTurn,
} from '@/features/courses/types'

// Intake
export const startIntake = (goal: string) => apiPost<IntakeSession>('/intake', { goal })
export const answerIntake = (id: string, answer: string) =>
  apiPost<IntakeSession>(`/intake/${id}/answer`, { answer })
export const getIntake = (id: string) => apiGet<IntakeSession>(`/intake/${id}`)
export const listIntakes = () => apiGet<IntakeSummary[]>('/intake')

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
export const unlockTopic = (lectureId: string, topicIndex: number) =>
  apiPost<LectureDetail>(`/lectures/${lectureId}/topics/${topicIndex}/unlock`)

// Quizzes
export const generateQuiz = (lectureId: string, topicIndex: number) =>
  apiPost<QuizView>(`/lectures/${lectureId}/topics/${topicIndex}/quiz`)
export const attemptQuiz = (lectureId: string, topicIndex: number, answers: number[]) =>
  apiPost<QuizResult>(`/lectures/${lectureId}/topics/${topicIndex}/quiz/attempt`, { answers })

// Ask DynoDoc (in-lesson tutor)
export const askTutor = (
  lectureId: string,
  topicIndex: number,
  question: string,
  history: TutorTurn[],
) =>
  apiPost<TutorReply>(`/lectures/${lectureId}/topics/${topicIndex}/ask`, { question, history })
