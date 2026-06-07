import { useState } from 'react'

const DEMO = {
  name: 'Kern County Solar Demo',
  technology: 'solar',
  capacity_mw: 100,
  lat: 35.37,
  lon: -118.83,
  state: 'CA',
  county: 'Kern',
  capex_millions: 120,
  placed_in_service_date: '2025-01-01',
  prevailing_wage_compliant: true,
  apprenticeship_compliant: true,
  domestic_content_pct: 45,
  ppa_rate_dollars_per_mwh: 65,
  discount_rate: 0.08,
  project_life_years: 25,
}

function Field({ label, hint, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">
        {label}
        {hint && <span className="text-slate-400 font-normal ml-1">({hint})</span>}
      </label>
      {children}
    </div>
  )
}

function Input({ ...props }) {
  return (
    <input
      {...props}
      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-900
                 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent
                 bg-white placeholder:text-slate-400"
    />
  )
}

function Select({ children, ...props }) {
  return (
    <select
      {...props}
      className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm text-slate-900
                 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent
                 bg-white"
    >
      {children}
    </select>
  )
}

function Section({ title, children }) {
  return (
    <div>
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
        {title}
      </h3>
      <div className="grid grid-cols-2 gap-4">
        {children}
      </div>
    </div>
  )
}

export default function IntakeForm({ onSubmit }) {
  const [form, setForm] = useState(DEMO)
  const [loading, setLoading] = useState(false)

  function set(key, value) {
    setForm(f => ({ ...f, [key]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    const payload = {
      ...form,
      capacity_mw:          Number(form.capacity_mw),
      lat:                  Number(form.lat),
      lon:                  Number(form.lon),
      capex_millions:       Number(form.capex_millions),
      domestic_content_pct: Number(form.domestic_content_pct),
      discount_rate:        Number(form.discount_rate),
      project_life_years:   Number(form.project_life_years),
      ppa_rate_dollars_per_mwh: form.ppa_rate_dollars_per_mwh === ''
        ? null
        : Number(form.ppa_rate_dollars_per_mwh),
    }
    await onSubmit(payload)
    setLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">Project Analysis</h2>
        <p className="text-slate-500 mt-1 text-sm">
          Enter your project details to generate an IRA tax credit analysis and investment memo.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-sm divide-y divide-slate-100">

        {/* Project */}
        <div className="p-6 space-y-4">
          <Section title="Project">
            <div className="col-span-2">
              <Field label="Project name">
                <Input value={form.name} onChange={e => set('name', e.target.value)} required />
              </Field>
            </div>
            <Field label="Technology">
              <Select value={form.technology} onChange={e => set('technology', e.target.value)}>
                <option value="solar">Solar</option>
                <option value="wind_onshore">Wind — Onshore</option>
                <option value="wind_offshore">Wind — Offshore</option>
                <option value="geothermal">Geothermal</option>
                <option value="storage">Storage</option>
              </Select>
            </Field>
            <Field label="Capacity" hint="MW">
              <Input type="number" min="0" step="0.1" value={form.capacity_mw}
                onChange={e => set('capacity_mw', e.target.value)} required />
            </Field>
            <Field label="Placed in service date">
              <Input type="date" value={form.placed_in_service_date}
                onChange={e => set('placed_in_service_date', e.target.value)} required />
            </Field>
          </Section>
        </div>

        {/* Location */}
        <div className="p-6 space-y-4">
          <Section title="Location">
            <Field label="State" hint="2-letter code">
              <Input maxLength={2} value={form.state}
                onChange={e => set('state', e.target.value.toUpperCase())} required />
            </Field>
            <Field label="County">
              <Input value={form.county} onChange={e => set('county', e.target.value)} required />
            </Field>
            <Field label="Latitude">
              <Input type="number" step="0.0001" value={form.lat}
                onChange={e => set('lat', e.target.value)} required />
            </Field>
            <Field label="Longitude">
              <Input type="number" step="0.0001" value={form.lon}
                onChange={e => set('lon', e.target.value)} required />
            </Field>
          </Section>
        </div>

        {/* Financial */}
        <div className="p-6 space-y-4">
          <Section title="Financial">
            <Field label="CapEx" hint="$M">
              <Input type="number" min="0" step="0.1" value={form.capex_millions}
                onChange={e => set('capex_millions', e.target.value)} required />
            </Field>
            <Field label="PPA rate" hint="$/MWh — leave blank to use EIA prices">
              <Input type="number" min="0" step="0.01" value={form.ppa_rate_dollars_per_mwh}
                placeholder="Optional"
                onChange={e => set('ppa_rate_dollars_per_mwh', e.target.value)} />
            </Field>
            <Field label="Discount rate" hint="decimal">
              <Input type="number" min="0" max="1" step="0.001" value={form.discount_rate}
                onChange={e => set('discount_rate', e.target.value)} required />
            </Field>
            <Field label="Project life" hint="years">
              <Input type="number" min="1" max="40" value={form.project_life_years}
                onChange={e => set('project_life_years', e.target.value)} required />
            </Field>
          </Section>
        </div>

        {/* Compliance */}
        <div className="p-6 space-y-4">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
            IRA Compliance
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={form.prevailing_wage_compliant}
                onChange={e => set('prevailing_wage_compliant', e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
              <div>
                <span className="text-sm font-medium text-slate-700">Prevailing wage compliant</span>
                <p className="text-xs text-slate-400">Davis-Bacon rates paid to all construction workers</p>
              </div>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" checked={form.apprenticeship_compliant}
                onChange={e => set('apprenticeship_compliant', e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
              <div>
                <span className="text-sm font-medium text-slate-700">Apprenticeship compliant</span>
                <p className="text-xs text-slate-400">10–15% of labor hours from DOL-registered programs</p>
              </div>
            </label>
          </div>
          <div className="mt-4">
            <Field label="Domestic content" hint="% of components by cost">
              <Input type="number" min="0" max="100" step="0.1" value={form.domestic_content_pct}
                onChange={e => set('domestic_content_pct', e.target.value)} required />
            </Field>
          </div>
        </div>

        {/* Submit */}
        <div className="px-6 py-4 bg-slate-50 rounded-b-xl flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Analysis takes ~45 seconds — the pipeline runs 5 AI agents in sequence.
          </p>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-semibold
                       hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors shadow-sm"
          >
            {loading ? 'Starting…' : 'Run analysis →'}
          </button>
        </div>
      </form>
    </div>
  )
}
