"use client"
import React, { useState, useEffect } from 'react'

interface FeatureItem {
  id: string
  name: string
  category: string
  description: string
  keywords: string[]
}

const FEATURES: FeatureItem[] = [
  // Intelligence
  { id: 'intent-detect', name: 'Intent Detection', category: 'Intelligence', description: 'Detect user intent with confidence scoring', keywords: ['intent', 'detection', 'purpose'] },
  { id: 'bias-detect', name: 'Bias Detection', category: 'Intelligence', description: 'Detect cognitive biases in text', keywords: ['bias', 'cognitive', 'psychology'] },
  { id: 'decision-analyze', name: 'Decision Analysis', category: 'Intelligence', description: 'Analyze decisions for blind spots and second-order effects', keywords: ['decision', 'analysis', 'blind spots'] },
  { id: 'contradiction-check', name: 'Contradiction Detection', category: 'Intelligence', description: 'Find contradictions in statements', keywords: ['contradiction', 'inconsistency', 'logic'] },
  
  // Agents
  { id: 'agent-create', name: 'Create Agent', category: 'Agents', description: 'Create automated AI agents', keywords: ['agent', 'automation', 'create'] },
  { id: 'agent-manage', name: 'Manage Agents', category: 'Agents', description: 'View and control your agents', keywords: ['agent', 'manage', 'control'] },
  
  // Tools
  { id: 'tool-permissions', name: 'Tool Permissions', category: 'Tools', description: 'Manage tool access permissions', keywords: ['tool', 'permissions', 'access'] },
  { id: 'tool-health', name: 'Tool Health', category: 'Tools', description: 'Monitor tool availability', keywords: ['tool', 'health', 'status'] },
  
  // Web
  { id: 'web-search', name: 'Web Search', category: 'Web', description: 'Search the web with citations', keywords: ['search', 'web', 'google'] },
  { id: 'credibility-check', name: 'Credibility Check', category: 'Web', description: 'Check source credibility', keywords: ['credibility', 'trust', 'source'] },
  { id: 'fact-check', name: 'Fact Check', category: 'Web', description: 'Verify claims against sources', keywords: ['fact', 'verify', 'truth'] },
  
  // Markets
  { id: 'earnings-analyze', name: 'Earnings Analysis', category: 'Markets', description: 'Analyze company earnings reports', keywords: ['earnings', 'stocks', 'analysis'] },
  { id: 'portfolio-analyze', name: 'Portfolio Analysis', category: 'Markets', description: 'Analyze investment portfolio', keywords: ['portfolio', 'investment', 'risk'] },
  { id: 'crypto-risk', name: 'Crypto Risk Scanner', category: 'Markets', description: 'Scan crypto for scams', keywords: ['crypto', 'scam', 'risk'] },
  
  // Health
  { id: 'wellness-track', name: 'Wellness Tracker', category: 'Health', description: 'Track wellness metrics', keywords: ['wellness', 'health', 'tracking'] },
  { id: 'nutrition-analyze', name: 'Nutrition Analysis', category: 'Health', description: 'Analyze diet and nutrition', keywords: ['nutrition', 'diet', 'food'] },
  { id: 'fitness-plan', name: 'Fitness Planner', category: 'Health', description: 'Create fitness plans', keywords: ['fitness', 'workout', 'exercise'] },
  
  // Education
  { id: 'learning-gaps', name: 'Learning Gap Detection', category: 'Education', description: 'Identify knowledge gaps', keywords: ['learning', 'gaps', 'study'] },
  { id: 'resume-analyze', name: 'Resume Analysis', category: 'Education', description: 'ATS-optimized resume review', keywords: ['resume', 'cv', 'job'] },
  { id: 'career-path', name: 'Career Path Planner', category: 'Education', description: 'Plan career transitions', keywords: ['career', 'path', 'transition'] },
  
  // Business
  { id: 'market-sizing', name: 'Market Sizing', category: 'Business', description: 'Calculate TAM/SAM/SOM', keywords: ['market', 'tam', 'sizing'] },
  { id: 'swot-analysis', name: 'SWOT Analysis', category: 'Business', description: 'Strategic SWOT analysis', keywords: ['swot', 'strategy', 'analysis'] },
  { id: 'gtm-plan', name: 'GTM Planning', category: 'Business', description: 'Go-to-market strategy', keywords: ['gtm', 'marketing', 'launch'] },
  
  // Personal OS
  { id: 'goals-manage', name: 'Goal Management', category: 'Personal', description: 'Track and decompose goals', keywords: ['goals', 'objectives', 'planning'] },
  { id: 'life-simulate', name: 'Life Simulation', category: 'Personal', description: 'Simulate life trajectories', keywords: ['life', 'simulation', 'future'] },
  { id: 'regret-minimize', name: 'Regret Minimization', category: 'Personal', description: 'Apply regret minimization framework', keywords: ['regret', 'decision', 'bezos'] },
  
  // Security
  { id: 'trust-score', name: 'Trust Score', category: 'Security', description: 'Calculate session trust', keywords: ['trust', 'security', 'safety'] },
  { id: 'privacy-explain', name: 'Privacy Explainer', category: 'Security', description: 'Explain privacy implications', keywords: ['privacy', 'data', 'gdpr'] },
]

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [search, setSearch] = useState('')
  const [filtered, setFiltered] = useState<FeatureItem[]>(FEATURES)
  const [selected, setSelected] = useState(0)

  useEffect(() => {
    if (!search.trim()) {
      setFiltered(FEATURES)
      return
    }

    const query = search.toLowerCase()
    const results = FEATURES.filter(f => 
      f.name.toLowerCase().includes(query) ||
      f.category.toLowerCase().includes(query) ||
      f.description.toLowerCase().includes(query) ||
      f.keywords.some(k => k.includes(query))
    )
    setFiltered(results)
    setSelected(0)
  }, [search])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelected(prev => Math.min(prev + 1, filtered.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelected(prev => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filtered[selected]) {
          handleSelect(filtered[selected])
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selected, filtered, onClose])

  const handleSelect = (feature: FeatureItem) => {
    console.log('Selected feature:', feature)
    // In real implementation, would trigger feature
    alert(`Feature: ${feature.name}\n\nThis would open ${feature.name} interface.`)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl mx-4">
        <div className="p-4 border-b">
          <input
            type="text"
            className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Search features... (try 'agent', 'health', 'market')"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No features found matching "{search}"
            </div>
          ) : (
            <ul>
              {filtered.map((feature, idx) => (
                <li
                  key={feature.id}
                  className={`p-4 border-b cursor-pointer transition-colors ${
                    idx === selected ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleSelect(feature)}
                  onMouseEnter={() => setSelected(idx)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">{feature.name}</div>
                      <div className="text-sm text-gray-600 mt-1">{feature.description}</div>
                      <div className="text-xs text-gray-400 mt-2">
                        Category: {feature.category}
                      </div>
                    </div>
                    {idx === selected && (
                      <div className="text-blue-500 ml-2">⏎</div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div className="p-3 bg-gray-50 text-xs text-gray-600 flex justify-between items-center rounded-b-lg">
          <div>
            <kbd className="px-2 py-1 bg-white border rounded">↑↓</kbd> Navigate
            <kbd className="ml-2 px-2 py-1 bg-white border rounded">↵</kbd> Select
            <kbd className="ml-2 px-2 py-1 bg-white border rounded">Esc</kbd> Close
          </div>
          <div>{filtered.length} results</div>
        </div>
      </div>
    </div>
  )
}

export default CommandPalette