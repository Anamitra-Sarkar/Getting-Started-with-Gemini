import { auth } from './firebase'
import { API_BASE } from './apiClient'

// Helper to get Firebase ID token
export async function getIdToken(): Promise<string | null> {
  try {
    const user = auth.currentUser
    if (!user) return null
    return await user.getIdToken()
  } catch (e) {
    console.error('Failed to get ID token:', e)
    return null
  }
}

// Helper for authenticated fetch
async function apiFetch(path: string, options?: RequestInit) {
  const token = await getIdToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })
  
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || `HTTP ${res.status}`)
  }
  
  return res.json()
}

// AI Generation
export async function aiGenerate(
  prompt: string,
  mode: string = 'chat',
  useSearch: boolean = false,
  convId?: number
) {
  return apiFetch('/ai/generate', {
    method: 'POST',
    body: JSON.stringify({
      prompt,
      mode,
      use_search: useSearch,
      conv_id: convId,
    }),
  })
}

// AI Streaming
export function streamAIGenerate(
  prompt: string,
  mode: string,
  useSearch: boolean,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
  onConvId?: (convId: number) => void,
  convId?: number
) {
  let stopped = false
  const controller = {
    stop: () => {
      stopped = true
    },
  }

  ;(async () => {
    try {
      const token = await getIdToken()
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const res = await fetch(`${API_BASE}/ai/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          prompt,
          mode,
          use_search: useSearch,
          conv_id: convId,
        }),
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const reader = res.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      while (!stopped) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (stopped) break
          if (!line.startsWith('data: ')) continue
          
          const data = line.slice(6)
          try {
            const json = JSON.parse(data)
            if (json.conv_id && onConvId) {
              onConvId(json.conv_id)
            }
            if (json.delta) {
              onChunk(json.delta)
            }
            if (json.done) {
              onDone()
              return
            }
            if (json.error) {
              onError(new Error(json.message || 'Stream error'))
              return
            }
          } catch (e) {
            // Skip malformed JSON
          }
        }
      }
      
      if (stopped) {
        reader.cancel()
      }
      onDone()
    } catch (err) {
      onError(err instanceof Error ? err : new Error(String(err)))
    }
  })()

  return controller
}

// Export Markdown
export async function exportMarkdown(convId: number): Promise<Blob> {
  const token = await getIdToken()
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}/export/markdown/${convId}`, {
    headers,
  })
  
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`)
  }
  
  return res.blob()
}

// Chains
export async function createChain(data: { name: string; definition?: string }) {
  return apiFetch('/chains', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listChains() {
  return apiFetch('/chains')
}

export async function runChain(chainId: number) {
  return apiFetch(`/chains/${chainId}/run`, {
    method: 'POST',
  })
}

// Memories
export async function createMemory(data: { content: string; long_term?: boolean }) {
  return apiFetch('/memories', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listMemories(longTerm: boolean = false) {
  return apiFetch(`/memories?long_term=${longTerm}`)
}

export async function updateMemory(memId: number, data: { content?: string; visible?: boolean; tags?: string[] }) {
  return apiFetch(`/memories/${memId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteMemory(memId: number) {
  return apiFetch(`/memories/${memId}`, {
    method: 'DELETE',
  })
}

// Projects
export async function createProject(data: { name: string; description?: string }) {
  return apiFetch('/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listProjects() {
  return apiFetch('/projects')
}

// Tasks
export async function createTask(data: { title: string; description?: string; project_id?: number; status?: string }) {
  return apiFetch('/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listTasks(projectId?: number) {
  const query = projectId ? `?project_id=${projectId}` : ''
  return apiFetch(`/tasks${query}`)
}

// Documents
export async function createDocument(data: { title: string; content: string }) {
  return apiFetch('/documents/create', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// Research
export async function tavilySearch(query: string) {
  return apiFetch('/research/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
}

export async function inspectCitation(url: string) {
  return apiFetch('/research/inspect', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}
