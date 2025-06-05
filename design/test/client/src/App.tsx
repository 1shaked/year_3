import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider, useMutation } from '@tanstack/react-query'
import './App.css'

const queryClient = new QueryClient()

function QuestionCountForm({ onSubmit }: { onSubmit: (count: number) => void }) {
  const [input, setInput] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const num = parseInt(input, 10)
    if (isNaN(num) || num < 1 || num > 20) {
      setError('Please enter a number between 1 and 20')
      return
    }
    setError('')
    onSubmit(num)
  }

  return (
    <form onSubmit={handleSubmit} style={{ margin: '2rem 0' }}>
      <label style={{ fontSize: '1.1rem' }}>
        Number of questions (1-20):
        <input
          type="number"
          min={1}
          max={20}
          value={input}
          onChange={e => setInput(e.target.value)}
          style={{ marginLeft: 8, fontSize: '1.5rem', width: 80, padding: '0.5rem' }}
        />
      </label>
      <div style={{ display: 'grid', justifyItems: 'center', marginTop: 16 }}>
        <button type="submit" style={{ marginLeft: 12, fontSize: '2rem', padding: '0.5rem 1.2rem', color: 'green',  }}>Start</button>
      </div>
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
    </form>
  )
}

// Types for the quiz API
export type QuizQuestion = {
  id: number
  question: string
  options: string[]
  correct_index: number
}


type QuizProps = {
  questions: QuizQuestion[]
}

function Quiz({ questions }: QuizProps) {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const handleSelect = (idx: number) => {
    if (!submitted) setSelected(idx)
  }

  const handleSubmit = () => {
    if (selected === null) return
    setAnswers([...answers, selected])
    setSubmitted(true)
  }

  const handleNext = () => {
    setSelected(null)
    setSubmitted(false)
    setCurrent(current + 1)
  }

  if (current >= questions.length) {
    const correctCount = answers.filter((ans, idx) => ans === questions[idx].correct_index).length;
    const grade = ((correctCount / questions.length) * 100).toFixed(1);
    let emoji = '';
    const gradeNum = parseFloat(grade);
    if (gradeNum >= 90) {
      emoji = '🏆';
    } else if (gradeNum >= 75) {
      emoji = '😃';
    } else if (gradeNum >= 60) {
      emoji = '🙂';
    } else if (gradeNum >= 40) {
      emoji = '😐';
    } else {
      emoji = '😢';
    }
    return (
      <div style={{ maxWidth: 700, margin: '2rem auto', background: '#f6f6f6', padding: 24, borderRadius: 12 }}>
        <h2 style={{ color: '#111' }}>Quiz Complete!</h2>
        <h3 style={{ color: '#111' }}>Report</h3>
        <div style={{ fontSize: '1.2rem', marginBottom: 16, color: '#111' }}>
          Grade: <b>{grade}</b> <span>{emoji}</span>
        </div>
        <button onClick={() => window.location.reload()} style={{ marginBottom: 24, background: '#007bff', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 24px', fontSize: '1rem', cursor: 'pointer' }}>
          Reset Test
        </button>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {questions.map((q, idx) => {
            const userAnswer = answers[idx]
            const isCorrect = userAnswer === q.correct_index
            return (
              <li
                key={q.id}
                style={{
                  marginBottom: 18,
                  background: isCorrect ? '#e6ffe6' : '#ffe6e6',
                  border: `1px solid ${isCorrect ? '#4caf50' : '#f44336'}`,
                  borderRadius: 8,
                  padding: '12px 16px',
                  color: isCorrect ? '#256029' : '#a94442',
                  fontWeight: isCorrect ? 'bold' : 'normal',
                  transition: 'box-shadow 0.3s, transform 0.3s',
                  boxShadow: 'none',
                  cursor: 'pointer',
                }}
                onMouseEnter={e => {
                  (e.currentTarget as HTMLLIElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
                  (e.currentTarget as HTMLLIElement).style.transform = 'scale(1.02)';
                }}
                onMouseLeave={e => {
                  (e.currentTarget as HTMLLIElement).style.boxShadow = 'none';
                  (e.currentTarget as HTMLLIElement).style.transform = 'scale(1)';
                }}
              >
                <div style={{ marginBottom: 6 }}>
                  {q.question}
                </div>
                <div>
                  Your answer: {q.options[userAnswer]}
                  {isCorrect ? (
                    <span style={{ marginLeft: 12, color: '#388e3c' }}>✔ Correct</span>
                  ) : (
                    <span style={{ marginLeft: 12, color: '#d32f2f' }}>✘ Wrong (Correct: {q.options[q.correct_index]})</span>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
      </div>
    )
  }

  const q = questions[current]

  return (
    <div style={{ margin: '2rem auto', maxWidth: 600, background: '#f6f6f6', padding: 24, borderRadius: 12, color: '#111' }}>
      <h3 style={{ color: '#111' }}>Question {current + 1} of {questions.length}</h3>
      <div style={{ fontSize: '1.2rem', marginBottom: 16, color: '#111' }}>{q.question}</div>
      <ul style={{ listStyle: 'none', padding: 0, textAlign: 'left' }}>
        {q.options.map((opt, idx) => (
          <li key={idx} style={{ marginBottom: 8 }}>
            <label style={{
              display: 'block',
              background: selected === idx ? '#d0eaff' : '#fff',
              border: '1px solid #ccc',
              borderRadius: 6,
              padding: '8px 12px',
              cursor: submitted ? 'default' : 'pointer',
              opacity: submitted && idx !== q.correct_index ? 0.6 : 1,
              fontWeight: submitted && idx === q.correct_index ? 'bold' : 'normal',
              color: '#111',
              textAlign: 'left',
            }}>
              <input
                type="radio"
                name={`q${current}`}
                value={idx}
                checked={selected === idx}
                disabled={submitted}
                onChange={() => handleSelect(idx)}
                style={{ marginRight: 8 }}
              />
              {opt}
            </label>
          </li>
        ))}
      </ul>
      {!submitted ? (
        <button onClick={handleSubmit} disabled={selected === null} style={{ marginTop: 16, background: '#007bff', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 24px', fontSize: '1rem' }}>
          Submit Answer
        </button>
      ) : (
        <button onClick={handleNext} style={{ marginTop: 16 }}>
          Next Question
        </button>
      )}
      {submitted && selected !== null && (
        <div style={{ marginTop: 12 }}>
          {selected === q.correct_index ? (
            <span style={{ color: 'green' }}>Correct!</span>
          ) : (
            <span style={{ color: 'red' }}>Incorrect. Correct answer: {q.options[q.correct_index]}</span>
          )}
        </div>
      )}
    </div>
  )
}

function QuizLoader({ questionCount }: { questionCount: number }) {
  const fetchQuestions = async (count: number): Promise<QuizQuestion[]> => {
    const res = await fetch(`/api/questions?num_questions=${count}`)
    if (!res.ok) throw new Error('Failed to fetch questions')
    return res.json()
  }

  const { mutate, data, isPending, isError, error } = useMutation<QuizQuestion[], Error, number>({
    mutationFn: fetchQuestions,
  })

  useEffect(() => {
    mutate(questionCount)
    // eslint-disable-next-line
  }, [questionCount])

  if (isPending) return <div>Loading questions...</div>
  if (isError) return <div style={{ color: 'red' }}>Error: {(error as Error).message}</div>
  if (!data) return null

  return <Quiz questions={data} />
}

const App = () => {
  const [questionCount, setQuestionCount] = useState<number | null>(null)

  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        {questionCount === null ? (
          <QuestionCountForm onSubmit={setQuestionCount} />
        ) : (
          <QuizLoader questionCount={questionCount} />
        )}
      </div>
    </QueryClientProvider>
  )
}

export default App
