"use client"
import React, { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Memories from './Memories'
import Projects from './Projects'
import TasksBoard from './TasksBoard'
import Chains from './Chains'
import AccountPanel from './AccountPanel'
import Composer from './Composer'
import ChatWindow from './ChatWindow'
import ResearchPanel from './ResearchPanel'
import CommandPalette from './CommandPalette'

export default function ChatWorkspace() {
  const [mode, setMode] = useState<'chat'|'think'|'study'|'code'|'document'>('chat')
  const [messages, setMessages] = useState<Array<{id:number, role:'user'|'assistant', content:string, streaming?:boolean}>>([])
  const [convId, setConvId] = useState<number | undefined>(undefined)
  const [showCommandPalette, setShowCommandPalette] = useState(false)

  useEffect(() => {
    // Command palette keyboard shortcut (Cmd+K or Ctrl+K)
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setShowCommandPalette(prev => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

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
        <div>
          <h1 className="text-3xl font-bold text-blue-600">Vaelis AI</h1>
          <p className="text-sm text-gray-500">General Intelligence Platform</p>
        </div>
        <div className="flex items-center gap-4">
          <button 
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
            onClick={() => setShowCommandPalette(true)}
          >
            ⌘K Command Palette
          </button>
          <div>Account · Theme</div>
        </div>
      </header>
      
      <div className="grid grid-cols-4 gap-6">
        <aside className="col-span-1 bg-white dark:bg-gray-800 p-4 rounded shadow h-fit sticky top-6">
          <Sidebar />
        </aside>
        
        <section className="col-span-3 bg-white dark:bg-gray-800 p-6 rounded shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-500">Current Mode:</div>
            <select value={mode} onChange={(e) => setMode(e.target.value as any)} className="border rounded p-2">
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
                <div className="h-72 border rounded p-4 overflow-auto bg-gray-50">
                  <h2 className="text-lg font-semibold mb-2">Conversation</h2>
                  <div className="space-y-3">
                    {messages.map((m) => (
                      <div key={m.id} className={m.role === 'assistant' ? 'bg-white p-3 rounded shadow-sm border' : 'text-right'}>
                        <div className="text-xs text-gray-500 mb-1">
                          {m.role === 'assistant' ? 'Vaelis' : 'You'}
                        </div>
                        <div className="whitespace-pre-wrap">{m.content || (m.streaming ? 'Thinking...' : '')}</div>
                      </div>
                    ))}
                    {messages.length === 0 && (
                      <div className="text-center py-12">
                        <div className="text-4xl mb-4">🧠</div>
                        <div className="text-gray-500">Start a conversation with Vaelis</div>
                        <div className="text-sm text-gray-400 mt-2">
                          Try: "Analyze this decision..." or press ⌘K for features
                        </div>
                      </div>
                    )}
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
                <div className="p-3 border rounded bg-gradient-to-br from-blue-50 to-purple-50">
                  <h3 className="font-semibold mb-2">Quick Actions</h3>
                  <div className="space-y-2 text-sm">
                    <button className="w-full text-left p-2 hover:bg-white rounded" onClick={() => setShowCommandPalette(true)}>
                      🎯 Launch Feature
                    </button>
                    <a href="#memories" className="block p-2 hover:bg-white rounded">
                      💭 Memories
                    </a>
                    <a href="#projects" className="block p-2 hover:bg-white rounded">
                      📁 Projects
                    </a>
                    <a href="#tasks" className="block p-2 hover:bg-white rounded">
                      ✅ Tasks
                    </a>
                    <a href="#chains" className="block p-2 hover:bg-white rounded">
                      🔗 Chains
                    </a>
                  </div>
                </div>
                
                <div className="p-3 border rounded">
                  <h3 className="font-semibold mb-2">System Status</h3>
                  <div className="text-xs space-y-1">
                    <div className="flex justify-between">
                      <span>AI Model:</span>
                      <span className="text-green-600">● Online</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Features:</span>
                      <span className="font-semibold">400</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active Agents:</span>
                      <span>0</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-2 gap-6">
              <div className="p-4 border rounded">
                {/* Memories component */}
                <div id="memories">
                  <Memories />
                </div>
              </div>
              <div className="p-4 border rounded space-y-4">
                <div id="projects">
                  <Projects />
                </div>
                <div id="tasks">
                  <TasksBoard />
                </div>
                <div id="chains">
                  <Chains />
                </div>
                <div>
                  <AccountPanel />
                </div>
                <div>
                  <ResearchPanel />
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
      
      <CommandPalette isOpen={showCommandPalette} onClose={() => setShowCommandPalette(false)} />
      
      <footer className="mt-8 text-center text-sm text-gray-500">
        <div>Vaelis AI — Production-Grade General Intelligence Platform</div>
        <div className="mt-1">400 Features | Agents | Tools | Intelligence | Personal OS</div>
      </footer>
    </div>
  )
}
