"use client"
import React, { useState, useRef } from 'react'
import { useToast } from './Toast'
import { aiGenerate, streamAIGenerate } from '@/lib/api'

export default function Composer({ onResult, onStart, onDone, onConv }: { onResult?: (out: string) => void; onStart?: (prompt: string) => void; onDone?: () => void; onConv?: (convId: number) => void }) {
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [partial, setPartial] = useState('')
  const streamRef = useRef<any>(null)
  const [useSearch, setUseSearch] = useState(false)
  const [convId, setConvId] = useState<number | undefined>(undefined)
  const toast = useToast()

  const send = async () => {
    onStart?.(value)
    setLoading(true)
    setPartial('')
    try {
      // try streaming first
      const controller = streamAIGenerate(
        value,
        'chat',
        useSearch,
        (chunk) => {
          setPartial((p) => {
            const next = p + chunk
            onResult?.(next)
            return next
          })
        },
        () => {
          setLoading(false)
          streamRef.current = null
          onDone?.()
        },
        (err) => {
          // fallback to non-stream on error
          console.error('Stream error', err)
          // Show toast error message
          try {
            toast.show('error', 'Stream failed, falling back')
          } catch (toastErr) {
            console.error('Toast error:', toastErr)
          }
          (async () => {
            try {
              const res = await aiGenerate(value, 'chat', false, convId)
              const out = res.output || JSON.stringify(res.raw || res)
              if (res.conv_id) {
                setConvId(res.conv_id)
                onConv?.(res.conv_id)
              }
              onResult?.(out)
            } catch (e: any) {
              onResult?.(`Error: ${e.message}`)
            } finally {
              setLoading(false)
            }
          })()
        },
        (cid: number) => {
          setConvId(cid)
          onConv?.(cid)
        },
        convId
      )
      streamRef.current = controller
    } catch (e: any) {
      onResult?.(`Error: ${e.message}`)
      setLoading(false)
    }
  }

  const stop = () => {
    if (streamRef.current) {
      streamRef.current.stop()
      streamRef.current = null
      setLoading(false)
    }
  }

  return (
    <div className="mt-4">
      <textarea value={value} onChange={(e) => setValue(e.target.value)} rows={6} className="w-full p-2 border rounded" />
      <div className="flex justify-between mt-2">
        <div className="text-sm text-gray-500">{loading ? 'Assistant is typing...' : ''}</div>
        <div>
          {loading ? (
            <button onClick={stop} className="px-4 py-2 bg-red-600 text-white rounded mr-2">Stop</button>
          ) : null}
          <button onClick={send} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
      {partial ? <div className="mt-2 p-2 bg-gray-50 rounded whitespace-pre-wrap">{partial}</div> : null}
    </div>
  )
}
