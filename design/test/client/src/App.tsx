import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Provider as JotaiProvider } from 'jotai'
import './App.css'
import './index.css'
import { QuestionCountForm } from './components/QuestionCountForm'
import { QuizLoader } from './components/QuizLoader'

const queryClient = new QueryClient()

const App = () => {
  const [questionCount, setQuestionCount] = useState<number | null>(null)

  return (
    <QueryClientProvider client={queryClient}>
      <JotaiProvider>
        <div className="App">
          {questionCount === null ? (
            <QuestionCountForm onSubmit={setQuestionCount} />
          ) : (
            <QuizLoader questionCount={questionCount} />
          )}
        </div>
      </JotaiProvider>
    </QueryClientProvider>
  )
}

export { App }
export default App
