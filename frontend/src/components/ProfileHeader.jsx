import { fmtNumber } from '../api/format'

export default function ProfileHeader({ profile }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">{profile.name || profile.ticker}
            <span className="text-slate-400 text-lg ml-2">{profile.ticker}</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {[profile.sector, profile.industry, profile.country].filter(Boolean).join(' · ')}
          </p>
        </div>
        <div className="text-right text-sm">
          {profile.cap_type && <span className="inline-block bg-brand/10 text-brand px-2 py-1 rounded text-xs font-semibold">{profile.cap_type}</span>}
          <p className="mt-1 text-slate-500">Market Cap: <strong>{fmtNumber(profile.market_cap)} {profile.currency || ''}</strong></p>
          {profile.website && <a href={profile.website} target="_blank" rel="noreferrer" className="text-brand text-xs hover:underline">{profile.website}</a>}
        </div>
      </div>
      {profile.description && (
        <p className="text-sm text-slate-600 mt-4 line-clamp-3">{profile.description}</p>
      )}
      {profile.sources?.length ? (
        <p className="text-xs text-slate-400 mt-3">Fuentes: {profile.sources.join(', ')}</p>
      ) : null}
    </div>
  )
}
