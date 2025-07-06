import { useAtom } from 'jotai'
import { useQuery } from '@tanstack/react-query'
import { selectedTopicIdAtom } from '../state'

/**
 * Topic selection dropdown component.
 */
export function TopicSelect() {
  const [selectedTopicId, setSelectedTopicId] = useAtom(selectedTopicIdAtom)
  const { data: topics, isLoading, isError, error } = useQuery<{ id: number; name: string }[], Error>({
    queryKey: ['topics'],
    queryFn: async () => {
      const isDev = import.meta.env.MODE === 'development'
      const API_BASE = isDev ? 'http://127.0.0.1:8000' : ''
      const res = await fetch(`${API_BASE}/api/topics`)
      if (!res.ok) throw new Error('Failed to fetch topics')
      return res.json()
    },
  })

  const containerStyle: React.CSSProperties = {
    margin: '1.5rem 0',
    padding: '1.2rem 1.5rem',
    border: '2px solid #888',
    borderRadius: 12,
    background: 'var(--topic-bg, #f8f9fa)',
    boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
    maxWidth: 400,
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

  if (isLoading) return <div style={containerStyle}>Loading topics...</div>
  if (isError) return <div style={{ ...containerStyle, color: 'red' }}>Error: {error?.message}</div>
  if (!topics || !topics.length) return <div style={containerStyle}>No topics found.</div>

  return (
    <div style={containerStyle}>
      <label style={{ fontSize: '1.15rem', fontWeight: 600, marginRight: 8, display: 'block', marginBottom: 10 }}>
        Select Topic:
        <select
          value={selectedTopicId ?? ''}
          onChange={e => setSelectedTopicId(e.target.value ? Number(e.target.value) : null)}
          style={{
            marginLeft: 0,
            marginTop: 8,
            fontSize: '1.1rem',
            padding: '0.5rem 1rem',
            borderRadius: 8,
            border: `1.5px solid ${borderColor}`,
            background: 'inherit',
            color: 'inherit',
            width: '100%',
            outline: 'none',
            boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
            transition: 'border 0.2s',
          }}
        >
          <option value="">-- Choose a topic --</option>
          {topics.map(t => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
      </label>
    </div>
  )
}
