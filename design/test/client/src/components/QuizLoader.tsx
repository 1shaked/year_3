import { useEffect } from 'react'
import { useAtom } from 'jotai'
import { useMutation } from '@tanstack/react-query'
import { selectedTopicIdAtom } from '../state'
import { Quiz } from './Quiz'
import type { QuizQuestionInterface } from '../types/QuizQuestion'

/**
 * Props interface for QuizLoader.
 */
export interface QuizLoaderPropsInterface {
  questionCount: number
}

/**
 * Loader for fetching and displaying quiz questions.
 */
export function QuizLoader(props: QuizLoaderPropsInterface) {
  const [selectedTopicId] = useAtom(selectedTopicIdAtom)
  const fetchQuestions = async (count: number): Promise<QuizQuestionInterface[]> => {
    if (!selectedTopicId) throw new Error('Please select a topic')
    const isDev = import.meta.env.MODE === 'development'
    const API_BASE = isDev ? 'http://127.0.0.1:8000' : ''
    const res = await fetch(`${API_BASE}/api/questions?num_questions=${count}&topic_id=${selectedTopicId}`)
    if (!res.ok) throw new Error('Failed to fetch questions')
    return res.json()
  }

  const { mutate, data, isPending, isError, error } = useMutation<QuizQuestionInterface[], Error, number>({
    mutationFn: fetchQuestions,
  })

  useEffect(() => {
    mutate(props.questionCount)
    // eslint-disable-next-line
  }, [props.questionCount])

  if (isPending) return <div>Loading questions...</div>
  if (isError) return <div style={{ color: 'red' }}>Error: {(error as Error).message}</div>
  if (!data) return null

  return <Quiz questions={data} />
}
