const ratingStyle = {
  Wide: 'bg-emerald-100 text-emerald-800',
  Narrow: 'bg-amber-100 text-amber-800',
  None: 'bg-red-100 text-red-800',
}

export default function QualitativePanel({ qualitative }) {
  const q = qualitative
  return (
    <section className="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-lg font-bold">Calidad del negocio (análisis cualitativo)</h2>
        <span className={`text-xs px-2 py-1 rounded ${q.ai_generated ? 'bg-brand text-white' : 'bg-slate-200 text-slate-700'}`}>
          {q.ai_generated ? 'Generado con IA' : 'Basado en reglas'} · Confianza: {q.confidence || '—'}
        </span>
      </div>

      {q.business_quality && (
        <p className="text-sm bg-slate-50 rounded-lg p-3"><strong>Clasificación:</strong> {q.business_quality}</p>
      )}

      {/* MOAT */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <h3 className="font-semibold text-brand">Ventaja competitiva (Moat)</h3>
          {q.moat.overall_rating && (
            <span className={`text-xs px-2 py-1 rounded font-semibold ${ratingStyle[q.moat.overall_rating] || 'bg-slate-100'}`}>
              {q.moat.overall_rating}
            </span>
          )}
          {q.moat.overall_score != null && (
            <span className="text-xs text-slate-500">{q.moat.overall_score.toFixed(0)}/100</span>
          )}
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {q.moat.types.map((t) => (
            <div key={t.name} className="border border-slate-200 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <p className="font-medium text-sm">{t.name}</p>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-100">{t.strength}</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{t.rationale}</p>
            </div>
          ))}
        </div>
        {q.moat.summary && <p className="text-sm text-slate-600 mt-3">{q.moat.summary}</p>}
      </div>

      {/* PORTER */}
      <div>
        <h3 className="font-semibold text-brand mb-3">5 Fuerzas de Porter</h3>
        <div className="space-y-2">
          {q.porter.forces.map((f) => (
            <div key={f.name} className="flex items-start gap-3 text-sm">
              <span className={`mt-0.5 text-xs px-2 py-0.5 rounded font-semibold shrink-0 ${
                f.intensity === 'Baja' ? 'bg-emerald-100 text-emerald-700'
                : f.intensity === 'Alta' ? 'bg-red-100 text-red-700'
                : 'bg-amber-100 text-amber-700'}`}>
                {f.intensity || '—'}
              </span>
              <div>
                <p className="font-medium">{f.name}</p>
                {f.rationale && <p className="text-xs text-slate-500">{f.rationale}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* MANAGEMENT */}
      <div>
        <h3 className="font-semibold text-brand mb-2">Equipo gestor</h3>
        {q.management.summary
          ? <p className="text-sm text-slate-600 whitespace-pre-line">{q.management.summary}</p>
          : (
            <ul className="text-sm text-slate-600 space-y-1">
              {q.management.capital_allocation && <li><strong>Asignación de capital:</strong> {q.management.capital_allocation}</li>}
              {q.management.operating_skill && <li><strong>Pericia operativa:</strong> {q.management.operating_skill}</li>}
              {q.management.alignment && <li><strong>Alineamiento:</strong> {q.management.alignment}</li>}
              {q.management.integrity && <li><strong>Integridad:</strong> {q.management.integrity}</li>}
            </ul>
          )}
      </div>
    </section>
  )
}
