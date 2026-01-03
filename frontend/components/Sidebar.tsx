"use client"
import React, { useState, useEffect } from 'react'
import { useToast } from './Toast'

const DEFAULT_TOOLS = {
  search: true,
  agents: false,
}

const Sidebar: React.FC = () => {
  const [mode, setMode] = useState('Chat')
  const [tools, setTools] = useState(DEFAULT_TOOLS)
  const toast = useToast()

  useEffect(() => {
    try {
      const raw = localStorage.getItem('vaelis_tools')
      if (raw) setTools(JSON.parse(raw))
    } catch (e) {
      // ignore
    }
  }, [])

  useEffect(() => {
    try { localStorage.setItem('vaelis_tools', JSON.stringify(tools)) } catch (e) {}
  }, [tools])

  const toggleTool = (k: string) => {
    const next = { ...tools, [k]: !((tools as any)[k]) }
    setTools(next)
    toast.show('info', `${k} ${(next as any)[k] ? 'enabled' : 'disabled'}`)
  }

  return (
    <div className="space-y-6 p-4 h-full overflow-y-auto">
      <div className="text-lg font-medium text-neutral-700 dark:text-neutral-300">Vaelis</div>
      
      <button 
        className="w-full text-left px-4 py-2.5 rounded-lg bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 hover:bg-neutral-800 dark:hover:bg-neutral-200 font-medium transition-colors"
        onClick={() => toast.show('info', 'New Chat started')}
      >
        + New Chat
      </button>

      <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
        <div className="text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wide mb-3">Mode</div>
        <ul className="space-y-1">
          {['Chat','Think','Study','Build'].map(m => (
            <li 
              key={m} 
              className={`px-3 py-2 cursor-pointer rounded-lg transition-colors ${
                mode===m
                  ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 font-medium'
                  : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50'
              }`} 
              onClick={() => { setMode(m); toast.show('info', `Mode: ${m}`) }}
            >
              {m}
            </li>
          ))}
        </ul>
      </div>
      
      <div className="border-t border-neutral-200 dark:border-neutral-700 pt-4">
        <div className="text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wide mb-3">Tools</div>
        <ul className="space-y-2">
          <li className="flex items-center justify-between px-3 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-lg transition-colors">
            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <span className="text-base">🔍</span>
              <span className="text-sm">Web Search</span>
            </div>
            <input 
              type="checkbox" 
              checked={tools.search} 
              onChange={() => toggleTool('search')}
              className="w-4 h-4 rounded accent-neutral-900 dark:accent-neutral-100" 
            />
          </li>
          <li className="flex items-center justify-between px-3 py-2 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 rounded-lg transition-colors">
            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <span className="text-base">🤖</span>
              <span className="text-sm">Agents</span>
            </div>
            <input 
              type="checkbox" 
              checked={tools.agents} 
              onChange={() => toggleTool('agents')}
              className="w-4 h-4 rounded accent-neutral-900 dark:accent-neutral-100" 
            />
          </li>
        </ul>
      </div>
    </div>
  )
}

export default Sidebar
