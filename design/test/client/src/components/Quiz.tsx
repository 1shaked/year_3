import { useState } from 'react'
import type { QuizPropsInterface } from '../types/QuizProps'
import { CopyIcon } from './CopyIcon'

/**
 * Quiz component for displaying questions and handling answers.
 */
export function Quiz(props: QuizPropsInterface) {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const [copyQFeedback, setCopyQFeedback] = useState(false)
  const [copyQAFeedback, setCopyQAFeedback] = useState(false)
  const [copyAllFeedback, setCopyAllFeedback] = useState(false)
  const [copyErrorsFeedback, setCopyErrorsFeedback] = useState(false)
  const [copyQReportFeedbackArr, setCopyQReportFeedbackArr] = useState<boolean[]>(Array(props.questions.length).fill(false))
  const q = props.questions[current]

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

  const handleCopyQuestion = () => {
    if (q) {
      void navigator.clipboard.writeText(q.question)
      setCopyQFeedback(true)
      setTimeout(() => setCopyQFeedback(false), 1200)
    }
  }

  const handleCopyQuestionAndAnswers = () => {
    if (q) {
      const text = `${q.question}\n${q.options.map((opt, idx) => `${String.fromCharCode(65 + idx)}. ${opt}`).join('\n')}`
      void navigator.clipboard.writeText(text)
      setCopyQAFeedback(true)
      setTimeout(() => setCopyQAFeedback(false), 1200)
    }
  }

  const handleCopyAllTest = () => {
    const allText = props.questions.map((q, idx) => {
      return `${idx + 1}. ${q.question}\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}${i === q.correct_index ? ' (Correct)' : ''}`).join('\n')}`
    }).join('\n\n')
    void navigator.clipboard.writeText(allText)
    setCopyAllFeedback(true)
    setTimeout(() => setCopyAllFeedback(false), 1200)
  }
  const handleCopyOnlyErrors = () => {
    const errorQs = props.questions.map((q, idx) => {
      if (answers[idx] !== q.correct_index) {
        return `${idx + 1}. ${q.question}\nYour answer: ${q.options[answers[idx]]}\nCorrect answer: ${q.options[q.correct_index]}\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}`).join('\n')}`
      }
      return null
    }).filter(Boolean).join('\n\n')
    void navigator.clipboard.writeText(errorQs)
    setCopyErrorsFeedback(true)
    setTimeout(() => setCopyErrorsFeedback(false), 1200)
  }

  if (current >= props.questions.length) {
    const correctCount = answers.filter((ans, idx) => ans === props.questions[idx].correct_index).length;
    const grade = ((correctCount / props.questions.length) * 100).toFixed(1);
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
        <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
          <div style={{ position: 'relative' }}>
            <button
              onClick={handleCopyAllTest}
              style={{
                background: copyAllFeedback ? '#28a745' : '#007bff',
                border: '1px solid #0056b3',
                borderRadius: 8,
                padding: '8px 18px',
                fontSize: '0.95rem',
                fontWeight: 500,
                cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                transition: 'background 0.2s, box-shadow 0.2s',
                outline: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              onMouseOver={e => {
                if (!copyAllFeedback) {
                  (e.currentTarget as HTMLButtonElement).style.background = '#0056b3';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
                }
              }}
              onMouseOut={e => {
                if (!copyAllFeedback) {
                  (e.currentTarget as HTMLButtonElement).style.background = '#007bff';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                }
              }}
              disabled={copyAllFeedback}
              title="Copy all test"
            >
              <CopyIcon color={copyAllFeedback ? '#fff' : '#fff'} size={20} /> 📋
            </button>
            {copyAllFeedback && (
              <span style={{
                position: 'absolute',
                left: '50%',
                top: '-28px',
                transform: 'translateX(-50%)',
                background: '#28a745',
                color: '#fff',
                padding: '2px 10px',
                borderRadius: 6,
                fontSize: '0.9rem',
                opacity: 1,
                transition: 'opacity 0.5s',
                pointerEvents: 'none',
                zIndex: 2,
              }}>
                Copied!
              </span>
            )}
          </div>
          <div style={{ position: 'relative' }}>
            <button
              onClick={handleCopyOnlyErrors}
              style={{
                background: copyErrorsFeedback ? '#28a745' : '#007bff',
                border: '1px solid #0056b3',
                borderRadius: 8,
                padding: '8px 18px',
                fontSize: '0.95rem',
                fontWeight: 500,
                cursor: 'pointer',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                transition: 'background 0.2s, box-shadow 0.2s',
                outline: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              onMouseOver={e => {
                if (!copyErrorsFeedback) {
                  (e.currentTarget as HTMLButtonElement).style.background = '#0056b3';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
                }
              }}
              onMouseOut={e => {
                if (!copyErrorsFeedback) {
                  (e.currentTarget as HTMLButtonElement).style.background = '#007bff';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                }
              }}
              disabled={copyErrorsFeedback}
              title="Copy only errors"
            >
              <CopyIcon color={copyErrorsFeedback ? '#fff' : '#fff'} size={20} /> ⚠️
            </button>
            {copyErrorsFeedback && (
              <span style={{
                position: 'absolute',
                left: '50%',
                top: '-28px',
                transform: 'translateX(-50%)',
                background: '#28a745',
                color: '#fff',
                padding: '2px 10px',
                borderRadius: 6,
                fontSize: '0.9rem',
                opacity: 1,
                transition: 'opacity 0.5s',
                pointerEvents: 'none',
                zIndex: 2,
              }}>
                Copied!
              </span>
            )}
          </div>
        </div>
        <h3 style={{ color: '#111' }}>Report</h3>
        <div style={{ fontSize: '1.2rem', marginBottom: 16, color: '#111' }}>
          Grade: <b>{grade}</b> <span>{emoji}</span>
        </div>
        <button onClick={() => window.location.reload()} style={{ marginBottom: 24, background: '#007bff', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 24px', fontSize: '1rem', cursor: 'pointer' }}>
          Reset Test
        </button>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {props.questions.map((q, idx) => {
            const userAnswer = answers[idx]
            const isCorrect = userAnswer === q.correct_index
            const handleCopyQReport = () => {
              const text = `${q.question}\n${q.options.map((opt, i) => `${String.fromCharCode(65 + i)}. ${opt}`).join('\n')}`
              void navigator.clipboard.writeText(text)
              setCopyQReportFeedbackArr(arr => {
                const newArr = [...arr]
                newArr[idx] = true
                return newArr
              })
              setTimeout(() => {
                setCopyQReportFeedbackArr(arr => {
                  const newArr = [...arr]
                  newArr[idx] = false
                  return newArr
                })
              }, 1200)
            }
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
                  position: 'relative',
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
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ flex: 1 }}>{q.question}</span>
                  <button
                    onClick={handleCopyQReport}
                    style={{
                      background: copyQReportFeedbackArr[idx] ? '#28a745' : 'transparent',
                      border: 'none',
                      borderRadius: 4,
                      padding: 4,
                      marginLeft: 8,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      transition: 'background 0.2s',
                    }}
                    title="Copy question and answers"
                    disabled={copyQReportFeedbackArr[idx]}
                  >
                    <CopyIcon color={copyQReportFeedbackArr[idx] ? '#fff' : '#1C274C'} size={20} /> Q&A
                  </button>
                  {copyQReportFeedbackArr[idx] && (
                    <span style={{
                      marginLeft: 6,
                      background: '#28a745',
                      color: '#fff',
                      borderRadius: 4,
                      padding: '2px 8px',
                      fontSize: '0.85rem',
                      transition: 'opacity 0.5s',
                    }}>Copied!</span>
                  )}
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

  return (
    <div style={{ margin: '2rem auto', maxWidth: 600, background: '#f6f6f6', padding: 24, borderRadius: 12, color: '#111' }}>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <div style={{ position: 'relative' }}>
          <button
            onClick={handleCopyQuestionAndAnswers}
            style={{
              background: copyQAFeedback ? '#28a745' : '#007bff',
              border: '1px solid #0056b3',
              borderRadius: 8,
              padding: '8px 18px',
              fontSize: '0.95rem',
              fontWeight: 500,
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              transition: 'background 0.2s, box-shadow 0.2s',
              outline: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onMouseOver={e => {
              if (!copyQAFeedback) {
                (e.currentTarget as HTMLButtonElement).style.background = '#0056b3';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
              }
            }}
            onMouseOut={e => {
              if (!copyQAFeedback) {
                (e.currentTarget as HTMLButtonElement).style.background = '#007bff';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
              }
            }}
            disabled={copyQAFeedback}
            title="Copy Q & Answers"
          >
            <CopyIcon color={copyQAFeedback ? '#fff' : '#fff'} size={20} /> Q&A
          </button>
          {copyQAFeedback && (
            <span style={{
              position: 'absolute',
              left: '50%',
              top: '-28px',
              transform: 'translateX(-50%)',
              background: '#28a745',
              color: '#fff',
              padding: '2px 10px',
              borderRadius: 6,
              fontSize: '0.9rem',
              opacity: 1,
              transition: 'opacity 0.5s',
              pointerEvents: 'none',
              zIndex: 2,
            }}>
              Copied!
            </span>
          )}
        </div>
        <div style={{ position: 'relative' }}>
          <button
            onClick={handleCopyQuestion}
            style={{
              background: copyQFeedback ? '#28a745' : '#007bff',
              border: '1px solid #0056b3',
              borderRadius: 8,
              padding: '8px 18px',
              fontSize: '0.95rem',
              fontWeight: 500,
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              transition: 'background 0.2s, box-shadow 0.2s',
              outline: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            onMouseOver={e => {
              if (!copyQFeedback) {
                (e.currentTarget as HTMLButtonElement).style.background = '#0056b3';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
              }
            }}
            onMouseOut={e => {
              if (!copyQFeedback) {
                (e.currentTarget as HTMLButtonElement).style.background = '#007bff';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
              }
            }}
            disabled={copyQFeedback}
            title="Copy Question"
          >
            <CopyIcon color={copyQFeedback ? '#fff' : '#fff'} size={20} /> ❔(Question)
          </button>
          {copyQFeedback && (
            <span style={{
              position: 'absolute',
              left: '50%',
              top: '-28px',
              transform: 'translateX(-50%)',
              background: '#28a745',
              color: '#fff',
              padding: '2px 10px',
              borderRadius: 6,
              fontSize: '0.9rem',
              opacity: 1,
              transition: 'opacity 0.5s',
              pointerEvents: 'none',
              zIndex: 2,
            }}>
              Copied!
            </span>
          )}
        </div>
      </div>
      <h3 style={{ color: '#111' }}>Question {current + 1} of {props.questions.length}</h3>
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
        <button
          onClick={handleNext}
          style={{
            marginTop: 16,
            background: '#007bff',
            color: '#fff',
            border: '1px solid #0056b3',
            borderRadius: 6,
            padding: '10px 24px',
            fontSize: '1rem',
            cursor: 'pointer',
            fontWeight: 500,
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            transition: 'background 0.2s, box-shadow 0.2s',
            outline: 'none',
          }}
          onMouseOver={e => {
            (e.currentTarget as HTMLButtonElement).style.background = '#0056b3';
            (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
          }}
          onMouseOut={e => {
            (e.currentTarget as HTMLButtonElement).style.background = '#007bff';
            (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
          }}
        >
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
