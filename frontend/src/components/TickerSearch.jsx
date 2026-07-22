import { useState } from 'react'

export default function TickerSearch({ onSearch, loading }) {
  const [ticker, setTicker] = useState('')
  const [useAi, setUseAi] = useState(true)

  const submit = (e) => {
    e.preventDefault()
    if (ticker.trim()) onSearch(ticker.trim().toUpperCase(), { useAi })
  }

  return (
    <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
      <input
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        placeholder="Introduce un ticker (AAPL, MSFT, IBE.MC...)"
        className="flex-1 px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand text-lg"
      />
      <label className="flex items-center gap-2 text-sm text-slate-600 select-none">
        <input type="checkbox" checked={useAi} onChange={(e) => setUseAi(e.target.checked)} />
        Análisis con IA
      </label>
      <button
        type="submit"
        disabled={loading}
        className="px-6 py-3 rounded-lg bg-brand hover:bg-brand-dark text-white font-semibold disabled:opacity-50"
      >
        {loading ? 'Analizando…' : 'Analizar'}
      </button>
    </form>
  )
}
