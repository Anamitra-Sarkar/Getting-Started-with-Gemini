"use client"
import React, { useState } from 'react'
import ChatWindow from '../../../components/ChatWindow'
import { getIdToken } from '@/lib/api'

export default function ConversationPage({ params }: { params: { id: string } }) {
  const id = parseInt(params.id, 10)
  const [showTags, setShowTags] = useState(false)
  const [tagInput, setTagInput] = useState('')

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto bg-white p-6 rounded shadow">
        <h2 className="text-lg font-semibold">Conversation {id}</h2>
        <div className="flex gap-2 mt-2">
          <button onClick={async ()=>{
            const token = await getIdToken()
            await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/conversations/${id}/pin`, {
              method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ pinned: true })
            })
          }} className="px-3 py-1 bg-yellow-400 rounded">Pin</button>
          <div>
            <button onClick={() => setShowTags(true)} className="px-3 py-1 bg-gray-200 rounded">Tags</button>
            {showTags && (
              <div className="mt-2 p-2 bg-gray-50 rounded shadow">
                <input value={tagInput} onChange={(e) => setTagInput(e.target.value)} placeholder="comma,separated,tags" className="border p-2 rounded w-full" />
                <div className="flex gap-2 mt-2">
                  <button onClick={async () => {
                    const token = await getIdToken()
                    await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/conversations/${id}/tags`, {
                      method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ tags: tagInput.split(',').map(s=>s.trim()).filter(Boolean) })
                    })
                    setShowTags(false)
                  }} className="px-3 py-1 bg-blue-600 text-white rounded">Save</button>
                  <button onClick={() => setShowTags(false)} className="px-3 py-1 border rounded">Cancel</button>
                </div>
              </div>
            )}
          </div>
          <button onClick={async ()=>{
            const token = await getIdToken()
            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/conversations/${id}/generate_title`, { method: 'POST', headers: { ...(token?{Authorization:`Bearer ${token}`}:{}) } })
            if (res.ok) {
              const j = await res.json()
              console.info('Generated title:', j.title)
            }
          }} className="px-3 py-1 bg-indigo-600 text-white rounded">Generate Title</button>
        </div>
        <div className="mt-4">
          <ChatWindow convId={id} />
        </div>
      </div>
    </main>
  )
}
