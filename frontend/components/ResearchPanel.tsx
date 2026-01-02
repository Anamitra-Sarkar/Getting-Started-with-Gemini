"use client"
import React, { useState } from 'react'
import { tavilySearch, inspectCitation } from '../lib/api'

export default function ResearchPanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [inspect, setInspect] = useState<any>(null)

  async function run() {
    const res = await tavilySearch(query)
    setResults(res.items || [])
  }

  async function doInspect(url: string) {
    const r = await inspectCitation(url)
    setInspect(r)
  }

  return (
    <div>
      <h2 className="text-lg font-semibold">Research</h2>
      <div className="mt-2 flex gap-2">
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search web (Tavily)" className="border p-2 flex-1" />
        <button onClick={run} className="bg-blue-600 text-white px-3 py-1 rounded">Search</button>
      </div>
      <ul className="mt-4">
        {results.map((it:any) => (
          <li key={it.url} className="border-b py-2">
            <div className="font-medium"><a href={it.url} target="_blank" rel="noreferrer" className="text-blue-600">{it.title}</a></div>
            <div className="text-sm">{it.snippet}</div>
            <div className="mt-1"><button onClick={() => doInspect(it.url)} className="border px-2 py-1 rounded">Inspect</button></div>
          </li>
        ))}
      </ul>
      {inspect && (
        <div className="mt-4 p-3 border rounded">
          <div className="font-semibold">Citation Inspector</div>
          <div>Title: {inspect.title}</div>
          <div>Description: {inspect.description}</div>
          <div>URL: <a href={inspect.url} target="_blank" rel="noreferrer">{inspect.url}</a></div>
        </div>
      )}
    </div>
  )
}
