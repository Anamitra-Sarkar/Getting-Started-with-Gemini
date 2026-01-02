"use client"
import React, { useState, useEffect } from 'react'
import { useToast } from './Toast'

const DEFAULT_TOOLS = {
  image: true,
  video: true,
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
    toast.show('info', `${k} ${next[k] ? 'enabled' : 'disabled'}`)
  }

  return (
    <div className="space-y-4 p-3">
      <button className="w-full text-left p-2 rounded hover:bg-gray-100">New Chat</button>
      <div className="border-t pt-2">Modes</div>
      <ul className="space-y-1">
        {['Chat','Think','Study','Build','Analyze'].map(m => (
          <li key={m} className={`p-1 cursor-pointer ${mode===m? 'font-semibold':''}`} onClick={() => { setMode(m); toast.show('info', `Mode: ${m}`) }}>{m}</li>
        ))}
      </ul>
      <div className="border-t pt-2">Tools</div>
      <ul className="space-y-1">
        <li className="flex items-center justify-between p-1"><div>Nano Banana (image)</div><input type="checkbox" checked={tools.image} onChange={() => toggleTool('image')} /></li>
        <li className="flex items-center justify-between p-1"><div>Veo 3.1 (video)</div><input type="checkbox" checked={tools.video} onChange={() => toggleTool('video')} /></li>
        <li className="flex items-center justify-between p-1"><div>Search</div><input type="checkbox" checked={tools.search} onChange={() => toggleTool('search')} /></li>
        <li className="flex items-center justify-between p-1"><div>Agents</div><input type="checkbox" checked={tools.agents} onChange={() => toggleTool('agents')} /></li>
      </ul>
    </div>
  )
}

export default Sidebar
