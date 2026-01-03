"use client"
import React, { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Composer from './Composer'
import ChatWindow from './ChatWindow'
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
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-950">
      <div className="max-w-7xl mx-auto flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-screen bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 sticky top-0">
          <Sidebar />
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 min-h-screen">
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {/* Header */}
            <header className="flex items-center justify-between py-4">
              <div>
                <h1 className="text-2xl font-medium text-neutral-900 dark:text-neutral-100">Vaelis</h1>
                <p className="text-sm text-neutral-500 dark:text-neutral-400">AI Workspace</p>
              </div>
              <button 
                className="px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
                onClick={() => setShowCommandPalette(true)}
              >
                ⌘K
              </button>
            </header>
            
            {/* Mode Selector */}
            <div className="flex gap-2">
              {['chat', 'think', 'study', 'code'].map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m as any)}
                  className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                    mode === m
                      ? 'bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 font-medium'
                      : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
                  }`}
                >
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </button>
              ))}
            </div>
            
            {/* Conversation Area */}
            <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 shadow-sm min-h-[500px] flex flex-col">
              <div className="flex-1 p-6 overflow-auto space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-center py-20">
                    <div>
                      <div className="text-5xl mb-4 opacity-20">💬</div>
                      <div className="text-neutral-500 dark:text-neutral-400">Start a conversation</div>
                      <div className="text-sm text-neutral-400 dark:text-neutral-500 mt-2">
                        Ask anything or press ⌘K for quick actions
                      </div>
                    </div>
                  </div>
                ) : (
                  messages.map((m) => (
                    <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-3xl px-4 py-3 rounded-xl ${
                        m.role === 'user'
                          ? 'bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900'
                          : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
                      }`}>
                        <div className="text-xs uppercase tracking-wide mb-1 opacity-60">
                          {m.role === 'assistant' ? 'Vaelis' : 'You'}
                        </div>
                        <div className="whitespace-pre-wrap">{m.content || (m.streaming ? 'Thinking...' : '')}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
              
              {/* Composer */}
              <div className="border-t border-neutral-200 dark:border-neutral-800 p-4">
                <Composer onStart={handleStart} onResult={handleResult} onDone={handleDone} onConv={(id) => setConvId(id)} />
              </div>
            </div>
            
            {/* Conversation Details (collapsed by default) */}
            {convId && (
              <details className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-800 shadow-sm">
                <summary className="px-6 py-4 cursor-pointer text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-xl transition-colors">
                  Conversation Details
                </summary>
                <div className="px-6 pb-6">
                  <ChatWindow convId={convId} />
                </div>
              </details>
            )}
          </div>
        </main>
      </div>
      
      <CommandPalette isOpen={showCommandPalette} onClose={() => setShowCommandPalette(false)} />
    </div>
  )
}
