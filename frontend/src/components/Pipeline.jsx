import { useEffect, useState } from 'react'

const STEPS = [
  { id: 'news',     label: 'News Agent',                  detail: 'Scanning IRS/Treasury updates and IRA policy news' },
  { id: 'credit',   label: 'Credit Identification Agent', detail: 'Determining ITC vs PTC election and base credit rate' },
  { id: 'adder',    label: 'Bonus Adder Agent',           detail: 'Checking energy community, domestic content eligibility' },
  { id: 'financial',label: 'Financial Model Agent',       detail: 'Running DCF — IRR, NPV, payback in two scenarios' },
  { id: 'memo',     label: 'Memo Agent',                  detail: 'Synthesizing results into investment memo' },
]

const STEP_DURATION = 9000   // ms per step (5 steps × 9s ≈ 45s total)

export default function Pipeline() {
  const [active, setActive] = useState(0)   // index of current step
  const [done, setDone]     = useState([])  // completed step indices

  useEffect(() => {
    if (active >= STEPS.length) return
    const timer = setTimeout(() => {
      setDone(d => [...d, active])
      setActive(a => a + 1)
    }, STEP_DURATION)
    return () => clearTimeout(timer)
  }, [active])

  return (
    <div className="max-w-xl mx-auto py-12">
      <div className="text-center mb-10">
        <h2 className="text-xl font-bold text-slate-900 mb-1">Analyzing project</h2>
        <p className="text-slate-500 text-sm">The agent pipeline is running — this takes about 45 seconds.</p>
      </div>

      <div className="space-y-3">
        {STEPS.map((step, i) => {
          const isDone    = done.includes(i)
          const isActive  = active === i
          const isPending = !isDone && !isActive

          return (
            <div
              key={step.id}
              className={`flex items-start gap-4 p-4 rounded-xl border transition-all duration-500 ${
                isDone   ? 'bg-emerald-50 border-emerald-200' :
                isActive ? 'bg-white border-slate-200 shadow-sm' :
                           'bg-white border-slate-100 opacity-40'
              }`}
            >
              {/* Icon */}
              <div className={`mt-0.5 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                isDone   ? 'bg-emerald-500' :
                isActive ? 'bg-slate-900' :
                           'bg-slate-200'
              }`}>
                {isDone ? (
                  <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : isActive ? (
                  <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-slate-400" />
                )}
              </div>

              {/* Text */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-semibold ${
                    isDone ? 'text-emerald-800' : isActive ? 'text-slate-900' : 'text-slate-400'
                  }`}>
                    {step.label}
                  </span>
                  {isDone && (
                    <span className="text-xs text-emerald-600 font-medium">Done</span>
                  )}
                  {isActive && (
                    <span className="text-xs text-slate-500 animate-pulse">Running…</span>
                  )}
                </div>
                <p className={`text-xs mt-0.5 ${
                  isDone ? 'text-emerald-600' : isActive ? 'text-slate-500' : 'text-slate-300'
                }`}>
                  {step.detail}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div className="mt-8 bg-slate-200 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-full bg-emerald-500 rounded-full transition-all duration-1000"
          style={{ width: `${Math.min(100, (done.length / STEPS.length) * 100)}%` }}
        />
      </div>
      <p className="text-center text-xs text-slate-400 mt-2">
        {done.length} of {STEPS.length} agents complete
      </p>
    </div>
  )
}
