'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import AppSidebar from '@/components/AppSidebar'

type StoredUser = {
  userId: string
  userType: string
  email: string
}

type RiskDistribution = {
  risk_distribution?: Record<string, number>
  total_incidents?: number
  average_risk_score?: number
}

type IncidentTypes = {
  incident_types?: Record<string, number>
  total_incidents?: number
}

type TimePatterns = {
  patterns?: Record<string, { incident_count: number; average_severity: number }>
  peak_hour?: string | null
}

type HeatmapData = {
  total_clusters?: number
  clusters?: Array<{
    cluster_id?: string
    risk_score?: number
    risk_level?: string
    incident_count?: number
    center_latitude?: number
    center_longitude?: number
    issue_types?: Record<string, number>
  }>
}

function formatLabel(value?: string) {
  return value ? value.replace(/_/g, ' ') : 'Not available'
}

function BarRow({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const width = max > 0 ? Math.max(6, Math.round((value / max) * 100)) : 0

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="font-semibold capitalize text-charcoal">{formatLabel(label)}</span>
        <span className="font-bold text-neutral">{value}</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-gray-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export default function HeatmapPage() {
  const router = useRouter()
  const [user, setUser] = useState<StoredUser | null>(null)
  const [riskDistribution, setRiskDistribution] = useState<RiskDistribution | null>(null)
  const [incidentTypes, setIncidentTypes] = useState<IncidentTypes | null>(null)
  const [timePatterns, setTimePatterns] = useState<TimePatterns | null>(null)
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('nagarseva_token')
    const storedUser = localStorage.getItem('nagarseva_user')

    if (!token || !storedUser) {
      router.replace('/auth')
      return
    }

    try {
      setUser(JSON.parse(storedUser))
    } catch {
      localStorage.removeItem('nagarseva_token')
      localStorage.removeItem('nagarseva_user')
      router.replace('/auth')
      return
    }

    setIsCheckingSession(false)
  }, [router])

  useEffect(() => {
    if (!user?.userId) {
      return
    }

    async function loadHeatmapData() {
      setIsLoading(true)
      setError('')

      try {
        const [riskResponse, typesResponse, timeResponse, heatmapResponse] = await Promise.all([
          fetch('/api/heatmap/analytics/risk-distribution?days_lookback=30', { cache: 'no-store' }),
          fetch('/api/heatmap/analytics/incident-types?days_lookback=30', { cache: 'no-store' }),
          fetch('/api/heatmap/analytics/time-patterns?days_lookback=30', { cache: 'no-store' }),
          fetch('/api/heatmap/data?days_lookback=30&eps_meters=500', { cache: 'no-store' }),
        ])

        const [riskData, typesData, timeData, mapData] = await Promise.all([
          riskResponse.json(),
          typesResponse.json(),
          timeResponse.json(),
          heatmapResponse.json(),
        ])

        setRiskDistribution(riskResponse.ok ? riskData : {})
        setIncidentTypes(typesResponse.ok ? typesData : {})
        setTimePatterns(timeResponse.ok ? timeData : {})
        setHeatmapData(heatmapResponse.ok ? mapData : {})

        if (!riskResponse.ok && !typesResponse.ok && !timeResponse.ok && !heatmapResponse.ok) {
          throw new Error('Unable to load heatmap analytics')
        }
      } catch (loadError) {
        setRiskDistribution({})
        setIncidentTypes({})
        setTimePatterns({})
        setHeatmapData({})
        setError(loadError instanceof Error ? loadError.message : 'Unable to load heatmap analytics')
      } finally {
        setIsLoading(false)
      }
    }

    loadHeatmapData()
  }, [user?.userId])

  const riskEntries = useMemo(
    () => Object.entries(riskDistribution?.risk_distribution || {}),
    [riskDistribution]
  )
  const incidentEntries = useMemo(
    () => Object.entries(incidentTypes?.incident_types || {}).filter(([, value]) => value > 0),
    [incidentTypes]
  )
  const timeEntries = useMemo(
    () => Object.entries(timePatterns?.patterns || {}),
    [timePatterns]
  )
  const maxRisk = Math.max(1, ...riskEntries.map(([, value]) => value))
  const maxIncident = Math.max(1, ...incidentEntries.map(([, value]) => value))
  const maxTime = Math.max(1, ...timeEntries.map(([, value]) => value.incident_count))

  if (isCheckingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-civic-light px-4">
        <div className="rounded-lg bg-white px-6 py-4 font-semibold text-charcoal shadow">
          Checking secure session...
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-civic-light lg:flex lg:items-start">
      <AppSidebar userEmail={user?.email} userType={user?.userType} userId={user?.userId} />

      <section className="min-w-0 flex-1 px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-civic">
            Heatmap Analytics
          </p>
          <h1 className="text-4xl font-bold text-charcoal">
            Risk clusters and incident patterns
          </h1>
          <p className="mt-3 max-w-3xl text-neutral">
            Analyze complaint risk by severity, issue type, time of day, and generated safety clusters.
          </p>
        </div>

        {error && (
          <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            ['Total Incidents', riskDistribution?.total_incidents ?? 0],
            ['Avg Risk Score', riskDistribution?.average_risk_score ?? 0],
            ['Risk Clusters', heatmapData?.total_clusters ?? 0],
            ['Peak Time', formatLabel(timePatterns?.peak_hour || 'none')],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
              <p className="text-sm font-semibold text-neutral">{label}</p>
              <p className="mt-2 text-3xl font-bold capitalize text-charcoal">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-2">
          <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-charcoal">Risk Distribution</h2>
                <p className="text-sm text-neutral">
                  {isLoading ? 'Loading...' : 'Severity mix from the last 30 days'}
                </p>
              </div>
              <Link href="/upload" className="rounded-xl bg-safety px-4 py-2 text-sm font-bold text-white">
                Upload
              </Link>
            </div>
            <div className="space-y-4">
              {riskEntries.map(([label, value]) => (
                <BarRow
                  key={label}
                  label={label}
                  value={value}
                  max={maxRisk}
                  color={
                    label === 'critical'
                      ? 'bg-red-500'
                      : label === 'high'
                      ? 'bg-safety'
                      : label === 'medium'
                      ? 'bg-trust'
                      : 'bg-civic'
                  }
                />
              ))}
            </div>
          </section>

          <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
            <h2 className="text-2xl font-bold text-charcoal">Incident Types</h2>
            <p className="mt-1 text-sm text-neutral">Most common civic issues in current data.</p>
            <div className="mt-5 space-y-4">
              {incidentEntries.length === 0 && (
                <p className="rounded-2xl bg-gray-50 p-4 text-sm font-semibold text-neutral">
                  No incident type data yet. Upload a classified report first.
                </p>
              )}
              {incidentEntries.map(([label, value]) => (
                <BarRow key={label} label={label} value={value} max={maxIncident} color="bg-civic" />
              ))}
            </div>
          </section>

          <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
            <h2 className="text-2xl font-bold text-charcoal">Time Patterns</h2>
            <p className="mt-1 text-sm text-neutral">Incident volume by time of day.</p>
            <div className="mt-5 space-y-4">
              {timeEntries.map(([label, data]) => (
                <BarRow
                  key={label}
                  label={`${label} (${data.average_severity})`}
                  value={data.incident_count}
                  max={maxTime}
                  color="bg-trust"
                />
              ))}
            </div>
          </section>

          <section className="rounded-3xl bg-charcoal p-6 text-white shadow-sm">
            <h2 className="text-2xl font-bold">Generated Clusters</h2>
            <p className="mt-1 text-sm text-white/65">DBSCAN-style risk clusters from complaint locations.</p>
            <div className="mt-5 space-y-3">
              {(heatmapData?.clusters || []).slice(0, 5).map((cluster, index) => (
                <div key={cluster.cluster_id || index} className="rounded-2xl bg-white/10 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-bold">Cluster {cluster.cluster_id || index + 1}</p>
                    <span className="rounded-full bg-safety px-3 py-1 text-xs font-bold text-white">
                      {formatLabel(cluster.risk_level)}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-white/70">
                    {cluster.incident_count || 0} incidents · score {cluster.risk_score || 0}
                  </p>
                </div>
              ))}
              {(heatmapData?.clusters || []).length === 0 && (
                <p className="rounded-2xl bg-white/10 p-4 text-sm font-semibold text-white/70">
                  No clusters generated yet. More geo-tagged complaints will make this more interesting.
                </p>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  )
}
