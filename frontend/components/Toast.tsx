"use client"
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'

type ToastItem = { id: number; type: 'info'|'success'|'error'; message: string }

type ToastContextType = {
  show: (type: ToastItem['type'], message: string) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const show = useCallback((type: ToastItem['type'], message: string) => {
    setToasts((t) => [...t, { id: Date.now() + Math.floor(Math.random()*1000), type, message }])
  }, [])

  useEffect(() => {
    if (toasts.length === 0) return
    const timers = toasts.map((t) => setTimeout(() => {
      setToasts((cur) => cur.filter(x => x.id !== t.id))
    }, 4500))
    return () => timers.forEach(clearTimeout)
  }, [toasts])

  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
        {toasts.map(t => (
          <div key={t.id} className={`px-4 py-2 rounded shadow text-sm max-w-xs break-words ${t.type === 'error' ? 'bg-red-600 text-white' : t.type === 'success' ? 'bg-green-600 text-white' : 'bg-gray-800 text-white'}`}>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextType {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

export default ToastProvider
