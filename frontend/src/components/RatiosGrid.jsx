import { fmtRatio, lightColor } from '../api/format'

export default function RatiosGrid({ ratios }) {
  const groups = [ratios.liquidity, ratios.activity, ratios.solvency, ratios.profitability]
  return (
    <section className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-bold mb-1">Ratios financieros</h2>
      <p className="text-xs text-slate-500 mb-4">
        Semáforo según rangos óptimos: <span className="inline-block w-3 h-3 rounded-full bg-emerald-500 align-middle" /> óptimo ·
        <span className="inline-block w-3 h-3 rounded-full bg-amber-400 align-middle ml-1" /> aceptable ·
        <span className="inline-block w-3 h-3 rounded-full bg-red-500 align-middle ml-1" /> riesgo
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        {groups.map((g) => (
          <div key={g.title}>
            <h3 className="font-semibold text-brand mb-2">{g.title}</h3>
            <table className="w-full text-sm">
              <tbody>
                {g.ratios.map((r) => (
                  <tr key={r.name} className="border-b border-slate-100">
                    <td className="py-2 pr-2">
                      <span className={`inline-block w-2.5 h-2.5 rounded-full mr-2 ${lightColor[r.light]}`} />
                      {r.name}
                    </td>
                    <td className="py-2 text-right font-semibold tabular-nums">{fmtRatio(r.latest, r.unit)}</td>
                    <td className="py-2 pl-3 text-right text-xs text-slate-400 hidden sm:table-cell">{r.optimal_range}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {ratios.roe_vs_roic_note && (
        <div className="mt-5 bg-slate-50 border-l-4 border-brand p-3 text-sm text-slate-700 rounded">
          <strong>ROE vs ROIC:</strong> {ratios.roe_vs_roic_note}
        </div>
      )}
    </section>
  )
}
