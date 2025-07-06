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

  if (isLoading) return <div>Loading topics...</div>
  if (isError) return <div style={{ color: 'red' }}>Error: {error?.message}</div>
  if (!topics || !topics.length) return <div>No topics found.</div>

  return (
    <div style={{ margin: '1rem 0' }}>
      <label style={{ fontSize: '1.1rem', marginRight: 8 }}>
        Select Topic:
        <select
          value={selectedTopicId ?? ''}
          onChange={e => setSelectedTopicId(e.target.value ? Number(e.target.value) : null)}
          style={{ marginLeft: 8, fontSize: '1.1rem', padding: '0.3rem 0.7rem' }}
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
