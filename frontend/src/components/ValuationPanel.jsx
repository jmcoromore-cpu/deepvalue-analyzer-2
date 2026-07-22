import { fmtMoney, fmtPct } from '../api/format'

export default function ValuationPanel({ valuation }) {
  return (
    <section className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-bold mb-4">Valoración (4 modelos)</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {valuation.models.map((m) => (
          <div key={m.name}
               className={`rounded-lg p-4 border ${m.included ? 'border-slate-200 bg-slate-50' : 'border-dashed border-slate-200 opacity-60'}`}>
            <p className="font-semibold">{m.name}</p>
            <p className="text-2xl font-bold text-brand">
              {m.included && m.value_per_share != null ? fmtMoney(m.value_per_share) : 'N/A'}
            </p>
            <p className="text-xs text-slate-500 mt-1">{m.detail}</p>
          </div>
        ))}
      </div>

      <div className="grid sm:grid-cols-4 gap-3 mt-5">
        <Box label="Valoración media" value={fmtMoney(valuation.mean_valuation)} strong />
        <Box label={`Precio máx. compra (margen ${(valuation.margin_of_safety * 100).toFixed(0)}%)`}
             value={fmtMoney(valuation.max_buy_price)} />
        <Box label="Precio actual" value={fmtMoney(valuation.current_price)} />
        <Box label="Potencial vs precio" value={fmtPct(valuation.upside_vs_price)}
             positive={valuation.upside_vs_price} />
      </div>
    </section>
  )
}

function Box({ label, value, strong, positive }) {
  const color = positive == null ? '' : positive >= 0 ? 'text-emerald-600' : 'text-red-600'
  return (
    <div className="text-center bg-slate-50 rounded-lg py-3 px-2">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`font-bold ${strong ? 'text-xl' : 'text-lg'} ${color}`}>{value}</p>
    </div>
  )
}
