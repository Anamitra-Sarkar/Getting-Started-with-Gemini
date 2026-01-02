"use client"
import React, { useEffect, useState } from 'react'
import { createChain, listChains, runChain } from '../lib/api'
import { useToast } from './Toast'

export default function Chains() {
  const [chains, setChains] = useState<any[]>([])
  const [name, setName] = useState('')

  async function load() {
    try {
      const res = await listChains()
      setChains(res.chains || [])
    } catch (e) { console.error(e) }
  }

  const toast = useToast()
  useEffect(() => { load() }, [])

  async function handleCreate() {
    if (!name) return
    await createChain({ name })
    setName('')
    await load()
  }

  async function handleRun(id: number) {
    try {
      await runChain(id)
      toast.show('success', 'Chain queued')
    } catch (e: any) {
      console.error(e)
      toast.show('error', e?.message || 'Failed to queue chain')
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold">Prompt Chains</h2>
      <div className="my-2 flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} className="border p-2 rounded flex-1" placeholder="Chain name" />
        <button onClick={handleCreate} className="bg-purple-600 text-white px-3 py-1 rounded">Create</button>
      </div>
      <ul>
        {chains.map(c => (
          <li key={c.id} className="border-b py-2 flex justify-between items-center">
            <div>
              <div className="font-medium">{c.name}</div>
              <div className="text-sm text-gray-500">{c.definition}</div>
            </div>
            <div>
              <button onClick={() => handleRun(c.id)} className="bg-yellow-600 text-white px-3 py-1 rounded">Run</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
