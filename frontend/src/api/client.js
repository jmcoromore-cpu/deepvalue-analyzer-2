const BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function analyzeTicker(ticker, opts = {}) {
  const params = new URLSearchParams()
  if (opts.marginOfSafety != null) params.set('margin_of_safety', opts.marginOfSafety)
  if (opts.discountRate != null) params.set('discount_rate', opts.discountRate)
  if (opts.useAi != null) params.set('use_ai', opts.useAi)
  const qs = params.toString()
  const url = `${BASE}/api/analyze/${encodeURIComponent(ticker)}${qs ? '?' + qs : ''}`
  const res = await fetch(url)
  if (!res.ok) {
    let detail = `Error ${res.status}`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch (e) { /* ignore */ }
    throw new Error(detail)
  }
  return res.json()
}
