import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import * as api from '@/features/courses/api'
import type { LectureDetail, TutorTurn } from '@/features/courses/types'

export const courseKeys = {
  all: ['courses'] as const,
  list: () => [...courseKeys.all, 'list'] as const,
  detail: (id: string) => [...courseKeys.all, 'detail', id] as const,
  lecture: (id: string) => ['lectures', id] as const,
}

export const intakeKeys = {
  all: ['intake'] as const,
  history: () => [...intakeKeys.all, 'history'] as const,
  session: (id: string) => [...intakeKeys.all, 'session', id] as const,
}

export const useCourses = () =>
  useQuery({ queryKey: courseKeys.list(), queryFn: api.listCourses })

export const useCourse = (id: string) =>
  useQuery({ queryKey: courseKeys.detail(id), queryFn: () => api.getCourse(id) })

export const useLecture = (id: string) =>
  useQuery({ queryKey: courseKeys.lecture(id), queryFn: () => api.getLecture(id) })

export const useIntakeHistory = () =>
  useQuery({ queryKey: intakeKeys.history(), queryFn: api.listIntakes })

export const useIntakeSession = (id: string | null) =>
  useQuery({
    queryKey: intakeKeys.session(id ?? ''),
    queryFn: () => api.getIntake(id as string),
    enabled: id !== null,
  })

export const useStartIntake = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.startIntake,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: intakeKeys.history() }),
  })
}

export const useAnswerIntake = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, answer }: { id: string; answer: string }) => api.answerIntake(id, answer),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: intakeKeys.history() }),
  })
}

export const useCreateCourse = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.createCourse,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: courseKeys.list() }),
  })
}

export const useGenerateTopic = (lectureId: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (topicIndex: number) => api.generateTopic(lectureId, topicIndex),
    onSuccess: (data: LectureDetail) =>
      queryClient.setQueryData(courseKeys.lecture(lectureId), data),
  })
}

export const useGenerateReferences = (lectureId: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => api.generateReferences(lectureId),
    onSuccess: (data: LectureDetail) =>
      queryClient.setQueryData(courseKeys.lecture(lectureId), data),
  })
}

export const useGenerateQuiz = (lectureId: string) =>
  useMutation({ mutationFn: (topicIndex: number) => api.generateQuiz(lectureId, topicIndex) })

export const useAttemptQuiz = (lectureId: string) => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ topicIndex, answers }: { topicIndex: number; answers: number[] }) =>
      api.attemptQuiz(lectureId, topicIndex, answers),
    onSuccess: () => {
      // Progress + unlock state changed — refetch the lecture and course views.
      void queryClient.invalidateQueries({ queryKey: courseKeys.lecture(lectureId) })
      void queryClient.invalidateQueries({ queryKey: courseKeys.all })
    },
  })
}

export const useAskTutor = (lectureId: string) =>
  useMutation({
    mutationFn: ({
      topicIndex,
      question,
      history,
    }: {
      topicIndex: number
      question: string
      history: TutorTurn[]
    }) => api.askTutor(lectureId, topicIndex, question, history),
  })
