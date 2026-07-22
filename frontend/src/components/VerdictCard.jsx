import { fmtMoney, fmtPct } from '../api/format'

const decisionStyle = {
  COMPRAR: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  MANTENER: 'bg-amber-100 text-amber-800 border-amber-300',
  EVITAR: 'bg-red-100 text-red-800 border-red-300',
}

export default function VerdictCard({ verdict, scoring, valuation }) {
  const style = decisionStyle[verdict.decision] || 'bg-slate-100'
  return (
    <div className={`rounded-xl border p-6 ${style}`}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-wide opacity-70">Veredicto</p>
          <p className="text-4xl font-black">{verdict.decision}</p>
          <p className="text-sm mt-1">Confianza: {verdict.confidence || '—'}</p>
        </div>
        <div className="text-right">
          <p className="text-sm uppercase tracking-wide opacity-70">Score global</p>
          <p className="text-4xl font-black">{scoring.final_score?.toFixed(0)}<span className="text-xl">/100</span></p>
          <div className="flex gap-3 text-xs mt-1 justify-end">
            <span>Cuant: {scoring.quant_score?.toFixed(0)}</span>
            <span>Cual: {scoring.qual_score?.toFixed(0)}</span>
          </div>
        </div>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-slate-700">{verdict.thesis}</p>

      <div className="grid sm:grid-cols-3 gap-4 mt-5 text-center">
        <Metric label="Valoración media" value={fmtMoney(valuation.mean_valuation, valuation && '')} />
        <Metric label="Precio actual" value={fmtMoney(valuation.current_price)} />
        <Metric label="Potencial" value={fmtPct(valuation.upside_vs_price)} />
      </div>

      {(verdict.strengths?.length || verdict.risks?.length) ? (
        <div className="grid sm:grid-cols-2 gap-4 mt-5">
          <List title="Fortalezas" items={verdict.strengths} color="text-emerald-700" />
          <List title="Riesgos" items={verdict.risks} color="text-red-700" />
        </div>
      ) : null}
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="bg-white/60 rounded-lg py-3">
      <p className="text-xs uppercase tracking-wide opacity-60">{label}</p>
      <p className="text-lg font-bold">{value}</p>
    </div>
  )
}

function List({ title, items, color }) {
  if (!items?.length) return null
  return (
    <div className="bg-white/60 rounded-lg p-4">
      <p className={`font-semibold mb-2 ${color}`}>{title}</p>
      <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">
        {items.map((it, i) => <li key={i}>{it}</li>)}
      </ul>
    </div>
  )
}
