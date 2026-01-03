"use client"
import ChatWorkspace from '../components/ChatWorkspace'
import Composer from '../components/Composer'
import { useState } from 'react'

export default function Home() {
  const [last, setLast] = useState('')
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <ChatWorkspace />
      <div className="max-w-6xl mx-auto p-6">
        <Composer onResult={(o) => setLast(o)} />
        {last && <pre className="mt-4 bg-white p-4 rounded shadow">{last}</pre>}
      </div>
    </main>
  )
}
