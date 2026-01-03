"use client"
import React, { useEffect, useState } from 'react'
import { createProject, listProjects } from '@/lib/api'
import { useToast } from './Toast'

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([])
  const [name, setName] = useState('')

  async function load() {
    try {
      const res = await listProjects()
      setProjects(res.projects || [])
    } catch (e) { console.error(e) }
  }

  useEffect(() => { load() }, [])

  const toast = useToast()

  async function handleCreate() {
    if (!name) return
    await createProject({ name })
    setName('')
    await load()
  }

  return (
    <div>
      <h2 className="text-lg font-semibold">Projects</h2>
      <div className="my-2 flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} className="border p-2 rounded flex-1" placeholder="New project name" />
        <button onClick={handleCreate} className="bg-green-600 text-white px-3 py-1 rounded">Create</button>
      </div>
      <ul>
        {projects.map(p => (
          <li key={p.id} className="border-b py-2">
            <div className="font-medium">{p.name}</div>
            <div className="text-sm text-gray-500">{p.description}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
