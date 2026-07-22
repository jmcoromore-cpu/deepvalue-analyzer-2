export function fmtNumber(v, digits = 0) {
  if (v == null || Number.isNaN(v)) return '—'
  const abs = Math.abs(v)
  if (abs >= 1e12) return (v / 1e12).toFixed(2) + ' B'  // billón (europeo)
  if (abs >= 1e9) return (v / 1e9).toFixed(2) + ' mM'
  if (abs >= 1e6) return (v / 1e6).toFixed(2) + ' M'
  if (abs >= 1e3) return (v / 1e3).toFixed(1) + ' k'
  return v.toFixed(digits)
}

export function fmtPct(v, digits = 1) {
  if (v == null || Number.isNaN(v)) return '—'
  return (v * 100).toFixed(digits) + '%'
}

export function fmtMoney(v, currency = '') {
  if (v == null || Number.isNaN(v)) return '—'
  return `${v.toFixed(2)}${currency ? ' ' + currency : ''}`
}

export function fmtRatio(v, unit) {
  if (v == null || Number.isNaN(v)) return '—'
  if (unit === '%') return fmtPct(v)
  if (unit === 'x') return v.toFixed(2) + '×'
  if (unit === 'días') return v.toFixed(0) + ' d'
  return v.toFixed(2)
}

export const lightColor = {
  green: 'bg-emerald-500',
  amber: 'bg-amber-400',
  red: 'bg-red-500',
  neutral: 'bg-slate-300',
}
