import ConversationList from '../../components/ConversationList'
import ChatWindow from '../../components/ChatWindow'
import { useState } from 'react'

export default function Recents() {
  const [selected, setSelected] = useState<number | undefined>()
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto grid grid-cols-4 gap-6">
        <aside className="col-span-1 bg-white p-4 rounded shadow">
          <ConversationList onSelect={(id) => setSelected(id)} />
        </aside>
        <section className="col-span-3 bg-white p-6 rounded shadow">
          <ChatWindow convId={selected} />
        </section>
      </div>
    </main>
  )
}
