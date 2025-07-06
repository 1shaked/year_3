import { useState } from 'react'
import { TopicSelect } from './TopicSelect'

/**
 * Props interface for QuestionCountForm.
 */
export interface QuestionCountFormPropsInterface {
  onSubmit: (count: number) => void
}

/**
 * Form for selecting the number of quiz questions.
 */
export function QuestionCountForm(props: QuestionCountFormPropsInterface) {
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
    props.onSubmit(num)
  }

  return (
    <>
      <TopicSelect />
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
          <button type="submit" style={{ marginLeft: 12, fontSize: '2rem', padding: '0.5rem 1.2rem', color: 'green' }}>Start</button>
        </div>
        {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
      </form>
    </>
  )
}
