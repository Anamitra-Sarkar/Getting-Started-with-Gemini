"use client"
import React, { useState } from 'react'
import { createDocument } from '@/lib/api'
import { useToast } from './Toast'

export default function DocumentStudio() {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const toast = useToast()

  async function createDoc() {
    if (!title) return
    try {
      await createDocument({ title, content })
      setTitle('')
      setContent('')
      toast.show('success', 'Document created')
    } catch (e: any) {
      console.error(e)
      toast.show('error', e?.message || 'Failed to create document')
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold">Document Studio</h2>
      <input className="w-full border p-2 my-2" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
      <textarea className="w-full border p-2 h-40" value={content} onChange={(e) => setContent(e.target.value)} placeholder="Content" />
      <div className="mt-2">
        <button onClick={createDoc} className="bg-blue-600 text-white px-3 py-1 rounded">Create</button>
      </div>
    </div>
  )
}
