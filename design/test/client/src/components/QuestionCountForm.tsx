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

  // Card style for form
  const containerStyle: React.CSSProperties = {
    margin: '2.5rem auto',
    padding: '2rem 2.5rem',
    border: '2px solid #888',
    borderRadius: 16,
    background: 'var(--form-bg, #f8f9fa)',
    boxShadow: '0 4px 16px rgba(0,0,0,0.09)',
    maxWidth: 420,
    color: 'inherit',
    transition: 'background 0.2s',
  }
  // Border color for both dark and light mode
  const borderColor = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? '#bbb'
    : '#888'
  containerStyle.border = `2px solid ${borderColor}`
  containerStyle.background = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? '#23272f'
    : '#f8f9fa'

  return (
    <div style={containerStyle}>
      <TopicSelect />
      <form onSubmit={handleSubmit} style={{ margin: '2rem 0 0 0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <label style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 14, width: '100%' }}>
          Number of questions (1-20):
          <input
            type="number"
            min={1}
            max={20}
            value={input}
            onChange={e => setInput(e.target.value)}
            style={{
              marginLeft: 0,
              marginTop: 10,
              fontSize: '1.3rem',
              width: '100%',
              padding: '0.6rem 1rem',
              borderRadius: 8,
              border: `1.5px solid ${borderColor}`,
              background: 'inherit',
              color: 'inherit',
              outline: 'none',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
              transition: 'border 0.2s',
            }}
          />
        </label>
        <button type="submit" style={{ marginTop: 18, fontSize: '1.3rem', padding: '0.7rem 2.2rem', color: '#fff', background: 'linear-gradient(90deg,#2ecc40,#0074d9)', border: 'none', borderRadius: 8, fontWeight: 700, cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>Start</button>
        {error && <div style={{ color: 'red', marginTop: 12, fontWeight: 500 }}>{error}</div>}
      </form>
    </div>
  )
}
