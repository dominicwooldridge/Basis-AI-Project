import { useState } from 'react'
import IntakeForm from './components/IntakeForm'
import Pipeline from './components/Pipeline'
import MemoCard from './components/MemoCard'

export default function App() {
  const [view, setView]   = useState('form')   // form | loading | result | error
  const [memo, setMemo]   = useState(null)
  const [error, setError] = useState(null)

  async function handleSubmit(project) {
    setView('loading')
    setError(null)
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(project),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `HTTP ${res.status}`)
      }
      setMemo(await res.json())
      setView('result')
    } catch (e) {
      setError(e.message)
      setView('error')
    }
  }

  function reset() {
    setView('form')
    setMemo(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <span className="text-white text-xl font-bold tracking-tight">Basis</span>
            <span className="text-slate-400 text-sm ml-3">IRA Deal Underwriting</span>
          </div>
          {view !== 'form' && (
            <button
              onClick={reset}
              className="text-slate-400 hover:text-white text-sm transition-colors"
            >
              ← New analysis
            </button>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        {view === 'form'    && <IntakeForm onSubmit={handleSubmit} />}
        {view === 'loading' && <Pipeline />}
        {view === 'result'  && <MemoCard memo={memo} onReset={reset} />}
        {view === 'error'   && (
          <div className="max-w-xl mx-auto bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <div className="text-red-500 text-4xl mb-3">⚠</div>
            <h2 className="text-red-900 font-semibold text-lg mb-2">Analysis failed</h2>
            <p className="text-red-700 text-sm mb-6">{error}</p>
            <button
              onClick={reset}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
            >
              Try again
            </button>
          </div>
        )}
      </main>

      {/* Footer disclaimer */}
      <footer className="border-t border-slate-200 bg-white mt-10">
        <div className="max-w-5xl mx-auto px-6 py-5">
          <p className="text-xs text-slate-400 leading-relaxed">
            <span className="font-semibold text-slate-500">Disclaimer:</span> Basis is an
            AI-assisted research tool intended for informational and educational purposes only.
            It does not constitute legal, tax, or financial advice and should not be relied upon
            as a substitute for consultation with qualified tax counsel, attorneys, or financial
            advisors. Credit eligibility determinations involve complex legal and factual questions
            that require professional judgment. The developers of Basis make no representations or
            warranties regarding the accuracy, completeness, or fitness for any purpose of the
            analysis provided, and accept no liability for any losses, penalties, or damages
            arising from reliance on this tool.
          </p>
        </div>
      </footer>
    </div>
  )
}
