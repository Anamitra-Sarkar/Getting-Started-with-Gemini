"use client"
import React, { useEffect, useState } from 'react'
import { createMemory, listMemories, updateMemory, deleteMemory } from '@/lib/api'
import { useToast } from './Toast'

export default function Memories() {
  const [memories, setMemories] = useState<any[]>([])
  const [content, setContent] = useState('')

  async function load() {
    try {
      const res = await listMemories(false)
      setMemories(res.memories || [])
    } catch (e) {
      console.error(e)
      // Silently fail if backend not available
    }
  }

  useEffect(() => { load() }, [])

  async function handleCreate() {
    if (!content) return
    await createMemory({ content })
    setContent('')
    await load()
  }

  const toast = useToast()

  return (
    <div>
      <h2 className="text-lg font-semibold">Memories</h2>
      <div className="my-2">
        <textarea value={content} onChange={(e) => setContent(e.target.value)} className="w-full p-2 border rounded" placeholder="Save a short-term memory" />
        <div className="flex gap-2 mt-2">
          <button onClick={handleCreate} className="bg-blue-600 text-white px-3 py-1 rounded">Save</button>
          <button onClick={load} className="border px-3 py-1 rounded">Refresh</button>
        </div>
      </div>
      <ul>
        {memories.map((m) => (
          <li key={m.id} className="border-b py-2">
            <div className="flex justify-between">
              <div>{m.content}</div>
              <div className="text-sm text-gray-500">{new Date(m.created_at).toLocaleString()}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
