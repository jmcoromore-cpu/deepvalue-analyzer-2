import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts'
import { fmtNumber, fmtPct } from '../api/format'

export default function FinancialsChart({ financials }) {
  const years = [...financials.years].sort((a, b) => a - b)
  const d = financials.derived || {}

  const series = (key) => years.map((y) => ({
    year: y,
    value: d[key]?.values?.[y] ?? null,
  }))

  const revenue = series('revenue')
  const netIncome = series('net_income')
  const fcf = series('free_cash_flow')

  const combined = years.map((y) => ({
    year: y,
    Ingresos: d.revenue?.values?.[y] ?? null,
    'Beneficio Neto': d.net_income?.values?.[y] ?? null,
    FCF: d.free_cash_flow?.values?.[y] ?? null,
  }))

  return (
    <section className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-bold mb-4">Evolución financiera</h2>
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="h-64">
          <p className="text-sm font-semibold text-slate-600 mb-2">Ingresos · Beneficio · FCF</p>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={combined}>
              <XAxis dataKey="year" fontSize={12} />
              <YAxis tickFormatter={(v) => fmtNumber(v)} fontSize={11} width={55} />
              <Tooltip formatter={(v) => fmtNumber(v, 0)} />
              <Legend />
              <Bar dataKey="Ingresos" fill="#0f766e" />
              <Bar dataKey="Beneficio Neto" fill="#38bdf8" />
              <Bar dataKey="FCF" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="h-64">
          <p className="text-sm font-semibold text-slate-600 mb-2">FCF por acción</p>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series('fcf_per_share')}>
              <XAxis dataKey="year" fontSize={12} />
              <YAxis fontSize={11} width={45} />
              <Tooltip formatter={(v) => v?.toFixed(2)} />
              <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={2} name="FCF/acción" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <CagrTable derived={d} />
    </section>
  )
}

const CAGR_ROWS = [
  ['revenue', 'Ingresos'],
  ['net_income', 'Beneficio Neto'],
  ['free_cash_flow', 'Free Cash Flow'],
  ['fcf_per_share', 'FCF por acción'],
  ['total_equity', 'Patrimonio Neto'],
]

function CagrTable({ derived }) {
  return (
    <div className="mt-6 overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 border-b border-slate-200">
            <th className="text-left py-2">Partida</th>
            <th className="text-right py-2">Var. anual</th>
            <th className="text-right py-2">CAGR 5A</th>
            <th className="text-right py-2">CAGR 10A</th>
          </tr>
        </thead>
        <tbody>
          {CAGR_ROWS.map(([key, label]) => {
            const row = derived[key]
            if (!row) return null
            return (
              <tr key={key} className="border-b border-slate-100">
                <td className="py-2">{label}</td>
                <td className="py-2 text-right tabular-nums">{fmtPct(row.yoy)}</td>
                <td className="py-2 text-right tabular-nums">{fmtPct(row.cagr_5y)}</td>
                <td className="py-2 text-right tabular-nums">{fmtPct(row.cagr_10y)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
