"use client"
import React, { useState } from 'react'
import Sidebar from './Sidebar'
import Memories from './Memories'
import Projects from './Projects'
import TasksBoard from './TasksBoard'
import Chains from './Chains'
import AccountPanel from './AccountPanel'
import Composer from './Composer'
import ChatWindow from './ChatWindow'
import ResearchPanel from './ResearchPanel'

export default function ChatWorkspace() {
  const [mode, setMode] = useState<'chat'|'think'|'study'|'code'|'document'>('chat')
  const [messages, setMessages] = useState<Array<{id:number, role:'user'|'assistant', content:string, streaming?:boolean}>>([])
  const [convId, setConvId] = useState<number | undefined>(undefined)

  function handleStart(prompt: string) {
    const userId = Date.now()
    setMessages((m) => [...m, { id: userId, role: 'user', content: prompt }])
    // insert assistant placeholder
    const assistantId = userId + 1
    setMessages((m) => [...m, { id: assistantId, role: 'assistant', content: '', streaming: true }])
  }

  function handleResult(partial: string) {
    setMessages((cur) => {
      const copy = [...cur]
      for (let i = copy.length - 1; i >= 0; i--) {
        if (copy[i].role === 'assistant') { copy[i] = { ...copy[i], content: partial }; break }
      }
      return copy
    })
  }

  function handleDone() {
    setMessages((cur) => cur.map(m => m.role === 'assistant' ? { ...m, streaming: false } : m))
  }
  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Vaelis</h1>
        <div>Account · Theme</div>
      </header>
      <div className="grid grid-cols-4 gap-6">
        <aside className="col-span-1 bg-white dark:bg-gray-800 p-4 rounded shadow">
          <Sidebar />
        </aside>
        <section className="col-span-3 bg-white dark:bg-gray-800 p-6 rounded shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-500">Mode:</div>
            <select value={mode} onChange={(e) => setMode(e.target.value as any)} className="border rounded p-1">
              <option value="chat">Chat</option>
              <option value="think">Think</option>
              <option value="study">Study</option>
              <option value="code">Code</option>
              <option value="document">Document</option>
            </select>
          </div>
          <div className="h-96">
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2">
                <div className="h-72 border rounded p-4 overflow-auto">
                  <h2 className="text-lg font-semibold mb-2">Conversation</h2>
                  <div className="space-y-3">
                    {messages.map((m) => (
                      <div key={m.id} className={m.role === 'assistant' ? 'bg-gray-100 p-3 rounded' : 'text-right'}>
                        <div className="text-xs text-gray-500">{m.role}</div>
                        <div className="whitespace-pre-wrap">{m.content}</div>
                      </div>
                    ))}
                    {messages.length === 0 && <div className="text-sm text-gray-500">No messages yet.</div>}
                  </div>
                </div>
                <div className="mt-4">
                  <Composer onStart={handleStart} onResult={handleResult} onDone={handleDone} onConv={(id) => setConvId(id)} />
                </div>
                <div className="mt-4">
                  <ChatWindow convId={convId} />
                </div>
              </div>
              <div className="col-span-1 space-y-4">
                <div className="p-3 border rounded">
                  <h3 className="font-semibold">Quick Actions</h3>
                  <div className="mt-2">
                    <a href="#memories" className="text-blue-600">Memories</a>
                    <br />
                    <a href="#projects" className="text-blue-600">Projects</a>
                    <br />
                    <a href="#tasks" className="text-blue-600">Tasks</a>
                    <br />
                    <a href="#chains" className="text-blue-600">Prompt Chains</a>
                    <br />
                    <a href="#account" className="text-blue-600">Account</a>
                  </div>
                </div>
                <div id="memories" className="p-3 border rounded">
                  <h3 className="font-semibold">Memories</h3>
                  <div className="mt-2">View and edit short-term memories.</div>
                </div>
                <div id="projects" className="p-3 border rounded">
                  <h3 className="font-semibold">Projects</h3>
                  <div className="mt-2">Project-scoped conversations and assets.</div>
                </div>
                <div id="account" className="p-3 border rounded">
                  <h3 className="font-semibold">Account</h3>
                  <div className="mt-2">Manage credits and billing.</div>
                </div>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-6">
              <div className="p-4 border rounded">
                {/* Memories component */}
                <div id="memories_section">
                  <Memories />
                </div>
              </div>
              <div className="p-4 border rounded">
                <Projects />
                <div className="mt-4">
                  <TasksBoard />
                </div>
                <div className="mt-4">
                  <Chains />
                </div>
                <div className="mt-4">
                  <AccountPanel />
                </div>
                  <div className="mt-4">
                    <ResearchPanel />
                  </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
