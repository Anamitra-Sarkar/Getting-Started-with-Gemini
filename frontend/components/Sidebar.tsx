"use client"
import React, { useState, useEffect } from 'react'
import { useToast } from './Toast'

const DEFAULT_TOOLS = {
  image: true,
  video: true,
  search: true,
  agents: false,
}

const FEATURE_CATEGORIES = [
  { id: 'intelligence', name: 'Intelligence', icon: '🧠', features: ['Intent Detection', 'Bias Detection', 'Decision Analysis'] },
  { id: 'agents', name: 'Agents', icon: '🤖', features: ['Create Agent', 'Manage Agents', 'Agent Memory'] },
  { id: 'tools', name: 'Tools', icon: '🔧', features: ['Tool Manager', 'Tool Permissions', 'Tool Health'] },
  { id: 'web', name: 'Web & News', icon: '🌐', features: ['Web Search', 'Credibility Check', 'Fact Check', 'News Heatmap'] },
  { id: 'markets', name: 'Markets', icon: '📈', features: ['Earnings Analysis', 'Portfolio Analysis', 'Crypto Risk'] },
  { id: 'health', name: 'Health', icon: '💪', features: ['Wellness', 'Nutrition', 'Fitness', 'Longevity'] },
  { id: 'education', name: 'Education', icon: '📚', features: ['Learning Gaps', 'Resume Analysis', 'Career Path'] },
  { id: 'business', name: 'Business', icon: '💼', features: ['Market Sizing', 'SWOT', 'GTM Planning', 'Pricing'] },
  { id: 'personal', name: 'Personal OS', icon: '🎯', features: ['Goals', 'Life Simulation', 'Regret Minimization'] },
  { id: 'security', name: 'Security', icon: '🔒', features: ['Trust Score', 'Privacy', 'Compliance'] },
]

const Sidebar: React.FC = () => {
  const [mode, setMode] = useState('Chat')
  const [tools, setTools] = useState(DEFAULT_TOOLS)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [view, setView] = useState<'main' | 'features'>('main')
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

  const toggleCategory = (id: string) => {
    setExpanded(expanded === id ? null : id)
  }

  return (
    <div className="space-y-4 p-3 h-full overflow-y-auto">
      <div className="text-xl font-bold text-blue-600">Vaelis AI</div>
      
      <button 
        className="w-full text-left p-2 rounded bg-blue-500 text-white hover:bg-blue-600 font-semibold"
        onClick={() => toast.show('info', 'New Chat started')}
      >
        + New Chat
      </button>

      <div className="flex gap-2">
        <button 
          className={`flex-1 p-1 text-sm rounded ${view === 'main' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
          onClick={() => setView('main')}
        >
          Main
        </button>
        <button 
          className={`flex-1 p-1 text-sm rounded ${view === 'features' ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
          onClick={() => setView('features')}
        >
          Features
        </button>
      </div>

      {view === 'main' ? (
        <>
          <div className="border-t pt-2 font-semibold text-sm text-gray-700">Modes</div>
          <ul className="space-y-1">
            {['Chat','Think','Study','Build','Analyze'].map(m => (
              <li 
                key={m} 
                className={`p-2 cursor-pointer rounded ${mode===m? 'bg-blue-100 font-semibold':'hover:bg-gray-100'}`} 
                onClick={() => { setMode(m); toast.show('info', `Mode: ${m}`) }}
              >
                {m}
              </li>
            ))}
          </ul>
          
          <div className="border-t pt-2 font-semibold text-sm text-gray-700">Core Tools</div>
          <ul className="space-y-1">
            <li className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
              <div className="flex items-center gap-2">
                <span>🖼️</span>
                <span>Nano Banana</span>
              </div>
              <input 
                type="checkbox" 
                checked={tools.image} 
                onChange={() => toggleTool('image')}
                className="w-4 h-4" 
              />
            </li>
            <li className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
              <div className="flex items-center gap-2">
                <span>🎬</span>
                <span>Veo 3.1</span>
              </div>
              <input 
                type="checkbox" 
                checked={tools.video} 
                onChange={() => toggleTool('video')}
                className="w-4 h-4" 
              />
            </li>
            <li className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
              <div className="flex items-center gap-2">
                <span>🔍</span>
                <span>Web Search</span>
              </div>
              <input 
                type="checkbox" 
                checked={tools.search} 
                onChange={() => toggleTool('search')}
                className="w-4 h-4" 
              />
            </li>
            <li className="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
              <div className="flex items-center gap-2">
                <span>🤖</span>
                <span>Agents</span>
              </div>
              <input 
                type="checkbox" 
                checked={tools.agents} 
                onChange={() => toggleTool('agents')}
                className="w-4 h-4" 
              />
            </li>
          </ul>
        </>
      ) : (
        <>
          <div className="border-t pt-2 font-semibold text-sm text-gray-700">
            400 Features Available
          </div>
          <div className="space-y-2">
            {FEATURE_CATEGORIES.map(category => (
              <div key={category.id} className="border rounded">
                <button
                  className="w-full text-left p-2 hover:bg-gray-50 flex items-center justify-between"
                  onClick={() => toggleCategory(category.id)}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{category.icon}</span>
                    <span className="font-medium">{category.name}</span>
                  </div>
                  <span>{expanded === category.id ? '▼' : '▶'}</span>
                </button>
                {expanded === category.id && (
                  <ul className="p-2 pt-0 space-y-1 text-sm">
                    {category.features.map((feature, idx) => (
                      <li 
                        key={idx}
                        className="p-1 hover:bg-gray-100 rounded cursor-pointer text-gray-700"
                        onClick={() => toast.show('info', `${feature} - Coming to chat soon!`)}
                      >
                        • {feature}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
          
          <div className="text-xs text-gray-500 pt-2 border-t">
            Navigate to any feature category to explore available capabilities.
          </div>
        </>
      )}
    </div>
  )
}

export default Sidebar
