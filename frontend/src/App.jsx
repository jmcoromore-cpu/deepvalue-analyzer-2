import { useState } from 'react'
import { analyzeTicker } from './api/client'
import TickerSearch from './components/TickerSearch'
import ProfileHeader from './components/ProfileHeader'
import VerdictCard from './components/VerdictCard'
import ValuationPanel from './components/ValuationPanel'
import RatiosGrid from './components/RatiosGrid'
import FinancialsChart from './components/FinancialsChart'
import QualitativePanel from './components/QualitativePanel'

export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (ticker, opts) => {
    setLoading(true); setError(''); setData(null)
    try {
      const result = await analyzeTicker(ticker, opts)
      setData(result)
    } catch (e) {
      setError(e.message || 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <header className="bg-brand text-white">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-black flex items-center gap-2">📊 DeepValue Analyzer</h1>
          <p className="text-sm text-teal-100 mt-1">
            Análisis fundamental exhaustivo a partir del ticker · valoración + calidad del negocio
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <TickerSearch onSearch={handleSearch} loading={loading} />
          <p className="text-xs text-slate-400 mt-3">
            Herramienta educativa. No es asesoramiento financiero. Los datos pueden contener imprecisiones según la fuente.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4">
            ⚠️ {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-16 text-slate-500">
            <div className="animate-spin w-10 h-10 border-4 border-brand border-t-transparent rounded-full mx-auto mb-4" />
            Analizando la empresa… (extrayendo datos, calculando ratios y valoraciones)
          </div>
        )}

        {data && !loading && (
          <div className="space-y-6">
            <ProfileHeader profile={data.profile} />

            {data.warnings?.length ? (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-3 text-sm">
                {data.warnings.map((w, i) => <p key={i}>ℹ️ {w}</p>)}
              </div>
            ) : null}

            <VerdictCard verdict={data.verdict} scoring={data.scoring} valuation={data.valuation} />
            <ValuationPanel valuation={data.valuation} />
            <QualitativePanel qualitative={data.qualitative} />
            <RatiosGrid ratios={data.ratios} />
            <FinancialsChart financials={data.financials} />

            <p className="text-xs text-slate-400 text-center pt-4">
              Generado el {data.generated_at}. DeepValue Analyzer — herramienta educativa, no constituye asesoramiento financiero.
            </p>
          </div>
        )}

        {!data && !loading && !error && (
          <div className="text-center py-16 text-slate-400">
            Introduce el ticker de una empresa para comenzar el análisis.
          </div>
        )}
      </main>
    </div>
  )
}
