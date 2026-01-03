"use client"
import React, { useEffect, useState } from 'react'
import { getIdToken } from '@/lib/api'
import { API_BASE } from '@/lib/apiClient'

export default function ConversationList({ onSelect }: { onSelect?: (id: number) => void }) {
  const [items, setItems] = useState<Array<{ id: number; title: string }>>([])
  const [filter, setFilter] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const token = await getIdToken()
        const res = await fetch(`${API_BASE}/conversations`, {
          headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        })
        if (res.ok) {
          const j = await res.json()
          // sort pinned first
          const convs = (j.conversations || []).sort((a: any,b: any)=> (b.pinned?1:0)-(a.pinned?1:0))
          setItems(convs)
        }
      } catch (e) {
        // ignore in scaffold
      }
    }
    load()
  }, [])

  return (
    <div className="space-y-2">
      <input placeholder="Filter tags" value={filter} onChange={(e)=>setFilter(e.target.value)} className="w-full p-2 border rounded mb-2" />
      {items.length === 0 && <div className="text-sm text-gray-500">No recent conversations</div>}
      {items.filter((c:any)=> !filter || (c.tags||'').includes(filter)).map((c:any) => (
        <button key={c.id} onClick={() => onSelect?.(c.id)} className="w-full text-left p-2 rounded hover:bg-gray-100">
          <div className="flex justify-between"><span>{c.title}</span>{c.pinned? <span className="text-xs text-yellow-600">Pinned</span>:null}</div>
          <div className="text-xs text-gray-400">{(c.tags||'').split(',').filter(Boolean).join(', ')}</div>
        </button>
      ))}
    </div>
  )
}
