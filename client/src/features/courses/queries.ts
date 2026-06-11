import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import * as api from '@/features/courses/api'
import type { LectureDetail } from '@/features/courses/types'

export const courseKeys = {
  all: ['courses'] as const,
  list: () => [...courseKeys.all, 'list'] as const,
  detail: (id: string) => [...courseKeys.all, 'detail', id] as const,
  lecture: (id: string) => ['lectures', id] as const,
}

export const useCourses = () =>
  useQuery({ queryKey: courseKeys.list(), queryFn: api.listCourses })

export const useCourse = (id: string) =>
  useQuery({ queryKey: courseKeys.detail(id), queryFn: () => api.getCourse(id) })

export const useLecture = (id: string) =>
  useQuery({ queryKey: courseKeys.lecture(id), queryFn: () => api.getLecture(id) })

export const useStartIntake = () => useMutation({ mutationFn: api.startIntake })

export const useAnswerIntake = () =>
  useMutation({
    mutationFn: ({ id, answer }: { id: string; answer: string }) => api.answerIntake(id, answer),
  })

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
