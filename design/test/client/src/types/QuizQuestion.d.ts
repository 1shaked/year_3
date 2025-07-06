/**
 * Interface for a quiz question.
 */
export interface QuizQuestionInterface {
  id: number
  question: string
  options: string[]
  correct_index: number
}
