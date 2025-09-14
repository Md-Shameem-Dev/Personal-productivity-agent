import React, { useState, useRef, useEffect } from 'react'

export default function App(){
  const [messages, setMessages] = useState([
    {role: 'bot', text: "Hi — I am LifePilot. I can schedule meetings, draft emails, and plan trips. Try: 'Schedule a meeting tomorrow at 3pm'."}
  ])
  const [input, setInput] = useState('')
  const chatRef = useRef(null)

  useEffect(()=> { chatRef.current?.scrollTo(0, chatRef.current.scrollHeight) }, [messages])

  const addMessage = (role, text) => setMessages(m => [...m, {role, text}])

  const send = async () => {
    const q = input.trim()
    if(!q) return
    addMessage('user', q)
    setInput('')
    try{
      const res = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({query: q})
      })
      const data = await res.json()
      // If the backend returns structured response, display message and store the structured payload for confirmation
      addMessage('bot', data.message || JSON.stringify(data))
      if(data.dry_run){
        // Save last action details on client to allow CONFIRM
        window.lastAction = { type: data.type, data: data.data }
      } else {
        window.lastAction = null
      }
    }catch(e){
      addMessage('bot', 'Error: cannot reach backend. Is it running?')
    }
  }

  const confirmAction = async () => {
    if(!window.lastAction) { addMessage('bot', 'Nothing to confirm'); return }
    const res = await fetch('http://127.0.0.1:8000/confirm', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(window.lastAction)
    })
    const data = await res.json()
    addMessage('bot', data.message || JSON.stringify(data))
    window.lastAction = null
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-blue-600 text-white py-4 px-6 font-semibold">🚀 LifePilot</div>
        <div ref={chatRef} className="p-4 h-96 overflow-y-auto">
          {messages.map((m,i)=> (
            <div key={i} className={`mb-3 flex ${m.role==='user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`px-4 py-2 rounded-lg max-w-[80%] ${m.role==='user' ? 'bg-blue-50 text-right' : 'bg-gray-100'}`}>
                <div style={{whiteSpace:'pre-wrap'}}>{m.text}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t flex gap-2">
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e => e.key==='Enter' && send()} className="flex-1 border rounded-lg px-3 py-2" placeholder="Ask LifePilot to do something..." />
          <button onClick={send} className="bg-blue-600 text-white px-4 py-2 rounded-lg">Send</button>
          <button onClick={confirmAction} className="bg-green-600 text-white px-3 py-2 rounded-lg">Confirm</button>
        </div>
      </div>
    </div>
  )
}
