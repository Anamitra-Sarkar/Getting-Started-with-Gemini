"use client"
import React, { useEffect, useState } from 'react'
import { getIdToken } from '../lib/api'

export default function AccountPanel() {
  const [account, setAccount] = useState<any>(null)
  const [amount, setAmount] = useState('')

  async function load() {
    try {
      const token = await getIdToken()
      const res = await fetch((process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000') + '/account/me', { headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) } })
      if (res.ok) setAccount(await res.json().then(r => r.account))
    } catch (e) {
      console.error(e)
      // Silently fail if backend not available
    }
  }

  useEffect(() => { load() }, [])

  async function add() {
    try {
      const token = await getIdToken()
      const res = await fetch((process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000') + '/account/credits/add', { method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ amount: Number(amount) }) })
      if (res.ok) {
        setAmount('')
        await load()
      }
    } catch (e) {
      console.error(e)
      // Silently fail if backend not available
    }
  }

  return (
    <div>
      <h3 className="font-semibold">Account</h3>
      {account ? (
        <div>
          <div>Credits: {account.credits}</div>
          <div className="mt-2 flex gap-2">
            <input value={amount} onChange={(e) => setAmount(e.target.value)} className="border p-1 rounded" placeholder="amount" />
            <button onClick={add} className="bg-blue-600 text-white px-3 py-1 rounded">Add Credits</button>
          </div>
        </div>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  )
}
