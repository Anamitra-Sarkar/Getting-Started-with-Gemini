"use client"
import React, { useEffect, useState } from 'react'
import { useToast } from './Toast'
import { exportMarkdown, getIdToken } from '@/lib/api'
import { API_BASE } from '@/lib/apiClient'

type ConvMeta = { id?: number; pinned?: boolean; tags?: string; title?: string }

export default function ChatWindow({ convId }: { convId?: number }) {
  const [messages, setMessages] = useState<any[]>([])
  const [selected, setSelected] = useState<Record<number, boolean>>({})
  const [meta, setMeta] = useState<ConvMeta | null>(null)
  const [tagInput, setTagInput] = useState<string>('')

  useEffect(() => {
    async function load() {
      if (!convId) return
      try {
        const token = await getIdToken()
        const res = await fetch(`${API_BASE}/conversations/${convId}`, {
          headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        })
        if (res.ok) {
          const j = await res.json()
          setMessages(j.messages || [])
          setMeta(j.conversation || null)
          setTagInput((j.conversation && j.conversation.tags) || '')
        }
      } catch (e) {
        console.error(e)
        toast.show('error', 'Failed to load conversation')
      }
    }
    load()
  }, [convId])

  const toast = useToast()

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-gray-600">{meta?.title ? meta.title : 'Conversation'}</div>
        {convId ? (
          <div className="flex items-center gap-2">
            <button onClick={async () => {
              try {
                const token = await getIdToken()
                const res = await fetch(`${API_BASE}/conversations/${convId}/pin`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
                  body: JSON.stringify({ pinned: !meta?.pinned })
                })
                if (res.ok) {
                  const j = await res.json()
                  setMeta((m) => ({ ...(m || {}), pinned: j.pinned }))
                }
              } catch (e) {
                console.error(e)
              }
            }} className={`px-3 py-1 rounded ${meta?.pinned ? 'bg-yellow-300' : 'border'}`}>
              {meta?.pinned ? 'Pinned' : 'Pin'}
            </button>
            <button onClick={async () => {
              try {
                const blob = await exportMarkdown(convId as number)
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `conversation-${convId}.md`
                a.click()
                URL.revokeObjectURL(url)
              } catch (e) { console.error(e) }
            }} className="px-3 py-1 bg-green-600 text-white rounded">Export</button>
            <button onClick={async () => {
              try {
                const token = await getIdToken()
                const res = await fetch(`${API_BASE}/conversations/${convId}/generate_title`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }
                })
                if (res.ok) {
                  const j = await res.json()
                  if (j.title) setMeta((m) => ({ ...(m || {}), title: j.title }))
                }
              } catch (e) { console.error(e) }
            }} className="px-3 py-1 bg-indigo-600 text-white rounded">Auto-title</button>
          </div>
        ) : null}
      </div>
      {messages.map((m: any, i: number) => (
        <div key={m.id || i} className={m.role === 'assistant' ? 'bg-gray-100 p-3 rounded' : 'text-right'}>
          <div className="flex items-center justify-between">
            <div className="text-xs text-gray-500">{m.role}</div>
            <div className="flex items-center gap-2">
              <input type="checkbox" checked={!!selected[m.id]} onChange={(e) => setSelected((s) => ({ ...s, [m.id]: e.target.checked }))} />
              {m.role === 'user' && (
                <button onClick={async () => {
                  try {
                    const token = await getIdToken()
                    const res = await fetch(`${API_BASE}/ai/retry`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
                      body: JSON.stringify({ conv_id: convId, message_id: m.id })
                    })
                    if (res.ok) {
                      const j = await res.json()
                      setMessages((cur) => [...cur, { id: Date.now(), role: 'assistant', content: j.result.output || JSON.stringify(j.result) }])
                    }
                  } catch (e) {
                        console.error(e)
                        toast.show('error', 'Retry failed')
                  }
                }} className="text-xs text-blue-600">Retry</button>
              )}
            </div>
          </div>
          <div className="whitespace-pre-wrap">{m.content}</div>
        </div>
      ))}
      {messages.length === 0 && <div className="text-sm text-gray-500">No messages yet.</div>}
      {convId && (
        <div className="mt-4 border-t pt-3">
          <div className="text-sm font-medium">Tags</div>
          <div className="flex gap-2 mt-2">
            <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="comma,separated,tags" className="border p-2 flex-1" />
            <button onClick={async () => {
              try {
                const token = await getIdToken()
                const tags = tagInput.split(',').map(s => s.trim()).filter(Boolean)
                const res = await fetch(`${API_BASE}/conversations/${convId}/tags`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
                  body: JSON.stringify({ tags })
                })
                if (res.ok) {
                  await res.json()
                  setMeta((m) => ({ ...(m || {}), tags: tags.join(',') }))
                }
              } catch (e) { console.error(e) }
            }} className="px-3 py-1 bg-blue-600 text-white rounded">Save</button>
          </div>
        </div>
      )}
      <div className="mt-4 flex gap-2">
        <button onClick={async () => {
          const ids = Object.keys(selected).filter(k => selected[Number(k)]).map(k => Number(k))
          if (ids.length === 0) return
          try {
            const token = await getIdToken()
            const res = await fetch(`${API_BASE}/export/messages`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
              body: JSON.stringify({ message_ids: ids })
            })
            if (res.ok) {
              const blob = await res.blob()
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `selected-${convId}.md`
              a.click()
              URL.revokeObjectURL(url)
            }
          } catch (e) { console.error(e) }
        }} className="px-3 py-1 bg-green-600 text-white rounded text-sm">Export Selected</button>
      </div>
    </div>
  )
}
