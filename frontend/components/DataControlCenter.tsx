"use client"
import React, { useEffect, useState } from 'react'
import { listMemories, deleteMemory } from '../lib/api'
import { useToast } from './Toast'

export default function DataControlCenter() {
  const [memories, setMemories] = useState<any[]>([])

  async function load() {
    try {
      const res = await listMemories(true)
      setMemories(res.memories || [])
    } catch (e) { console.error(e) }
  }

  useEffect(() => { load() }, [])

  async function forget(id: number) {
    await deleteMemory(id)
    await load()
  }

  const toast = useToast()

  return (
    <div>
      <h2 className="text-lg font-semibold">Data Control Center</h2>
      <div className="mt-2">Manage long-term memory and privacy settings.</div>
      <ul className="mt-4">
        {memories.map(m => (
          <li key={m.id} className="border-b py-2 flex justify-between items-center">
            <div>
              <div className="font-medium">{m.content}</div>
              <div className="text-sm text-gray-500">{m.tags}</div>
            </div>
            <div>
              <button onClick={() => forget(m.id)} className="bg-red-600 text-white px-3 py-1 rounded">Forget</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
