"use client"
import React, { useEffect, useState } from 'react'
import { createTask, listTasks } from '../lib/api'
import { useToast } from './Toast'

export default function TasksBoard() {
  const [tasks, setTasks] = useState<any[]>([])
  const [title, setTitle] = useState('')

  async function load() {
    try {
      const res = await listTasks()
      setTasks(res.tasks || [])
    } catch (e) { console.error(e) }
  }

  useEffect(() => { load() }, [])

  const toast = useToast()

  async function handleCreate() {
    if (!title) return
    await createTask({ title })
    setTitle('')
    await load()
  }

  return (
    <div>
      <h2 className="text-lg font-semibold">Tasks</h2>
      <div className="my-2 flex gap-2">
        <input value={title} onChange={(e) => setTitle(e.target.value)} className="border p-2 rounded flex-1" placeholder="New task title" />
        <button onClick={handleCreate} className="bg-indigo-600 text-white px-3 py-1 rounded">Add</button>
      </div>
      <ul>
        {tasks.map(t => (
          <li key={t.id} className="border-b py-2">
            <div className="font-medium">{t.title}</div>
            <div className="text-sm text-gray-500">Status: {t.status}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
