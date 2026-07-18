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

type Report = {
  _id?: string
  id?: string
  issue_title?: string
  status?: string
  classification?: {
    severity?: string
    issue_type?: string
  }
  dashboard_status?: {
    is_overdue?: boolean
    days_remaining?: number
    sla_days?: number
  }
  assignment?: {
    department?: string
    official_name?: string
    official_role?: string
  }
  escalation?: {
    is_escalated?: boolean
    latest_status?: string
    history?: Array<{
      escalation_level?: number
      status?: string
      created_at?: string
    }>
  }
}

type DashboardData = {
  reports: Report[]
}

type PendingCount = {
  pending_count?: number
  critical_count?: number
}

type EscalationRate = {
  total_complaints?: number
  total_escalated?: number
  escalation_rate_percent?: number
  escalation_levels?: Record<string, number>
}

function getReportId(report: Report) {
  return report._id || report.id || 'Pending ID'
}

function formatLabel(value?: string) {
  return value ? value.replace(/_/g, ' ') : 'Not available'
}

export default function EscalationPage() {
  const router = useRouter()
  const [user, setUser] = useState<StoredUser | null>(null)
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [pendingCount, setPendingCount] = useState<PendingCount | null>(null)
  const [escalationRate, setEscalationRate] = useState<EscalationRate | null>(null)
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
      const parsedUser = JSON.parse(storedUser) as StoredUser
      setUser(parsedUser)

      if (parsedUser.userId) {
        setIsLoading(true)
        setError('')

        Promise.all([
          fetch(`/api/complaints/citizen/${parsedUser.userId}/dashboard?limit=25`, {
            cache: 'no-store',
          }),
          fetch('/api/escalation/pending-count', { cache: 'no-store' }),
          fetch('/api/escalation/analytics/escalation-rate?days_lookback=30', {
            cache: 'no-store',
          }),
        ])
          .then(async ([dashboardResponse, pendingResponse, rateResponse]) => {
            const dashboardData = await dashboardResponse.json()
            const pendingData = await pendingResponse.json()
            const rateData = await rateResponse.json()

            if (!dashboardResponse.ok) {
              throw new Error(dashboardData.detail || 'Unable to load dashboard reports')
            }

            setDashboard(dashboardData)
            setPendingCount(pendingResponse.ok ? pendingData : {})
            setEscalationRate(rateResponse.ok ? rateData : {})
          })
          .catch((loadError) => {
            setDashboard({ reports: [] })
            setPendingCount({})
            setEscalationRate({})
            setError(
              loadError instanceof Error
                ? loadError.message
                : 'Unable to load escalation data'
            )
          })
          .finally(() => {
            setIsLoading(false)
          })
      }
    } catch {
      localStorage.removeItem('nagarseva_token')
      localStorage.removeItem('nagarseva_user')
      router.replace('/auth')
      return
    }

    setIsCheckingSession(false)
  }, [router])

  const escalatedReports = useMemo(
    () =>
      (dashboard?.reports || []).filter(
        (report) => report.escalation?.is_escalated || report.dashboard_status?.is_overdue
      ),
    [dashboard]
  )

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
            Escalation
          </p>
          <h1 className="text-4xl font-bold text-charcoal">
            Overdue and escalated complaints
          </h1>
          <p className="mt-3 max-w-3xl text-neutral">
            Track SLA breaches, pending escalations, critical complaints, and escalation levels.
          </p>
        </div>

        {error && (
          <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            ['Pending Escalations', pendingCount?.pending_count ?? 0],
            ['Critical Escalations', pendingCount?.critical_count ?? 0],
            ['Escalated In 30 Days', escalationRate?.total_escalated ?? 0],
            ['Escalation Rate', `${escalationRate?.escalation_rate_percent ?? 0}%`],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
              <p className="text-sm font-semibold text-neutral">{label}</p>
              <p className="mt-2 text-3xl font-bold text-charcoal">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-charcoal">Escalation Queue</h2>
              <p className="mt-1 text-sm text-neutral">
                {isLoading ? 'Loading escalation queue...' : `${escalatedReports.length} citizen reports need attention`}
              </p>
            </div>
            <Link
              href="/upload"
              className="rounded-xl bg-safety px-5 py-3 font-semibold text-white hover:bg-safety-dark"
            >
              Upload Report
            </Link>
          </div>

          {escalatedReports.length === 0 && !isLoading && (
            <p className="mt-6 rounded-2xl bg-green-50 p-4 text-sm font-semibold text-green-700">
              No overdue or escalated citizen reports right now.
            </p>
          )}

          <div className="mt-6 space-y-4">
            {escalatedReports.map((report) => (
              <article key={getReportId(report)} className="rounded-2xl border border-gray-100 bg-gray-50 p-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-neutral">
                      {getReportId(report)}
                    </p>
                    <h3 className="mt-2 text-xl font-bold text-charcoal">
                      {report.issue_title || 'Civic issue'}
                    </h3>
                    <p className="mt-1 text-sm text-neutral">
                      Assigned to {report.assignment?.official_name || report.assignment?.official_role || report.assignment?.department || 'municipal team'}
                    </p>
                  </div>
                  <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-700">
                    {report.dashboard_status?.is_overdue ? 'Overdue' : 'Escalated'}
                  </span>
                </div>

                <div className="mt-4 grid gap-3 sm:grid-cols-4">
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-bold uppercase text-neutral">Issue</p>
                    <p className="mt-1 text-sm font-bold capitalize text-charcoal">
                      {formatLabel(report.classification?.issue_type)}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-bold uppercase text-neutral">Severity</p>
                    <p className="mt-1 text-sm font-bold capitalize text-charcoal">
                      {formatLabel(report.classification?.severity)}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-bold uppercase text-neutral">SLA</p>
                    <p className="mt-1 text-sm font-bold text-charcoal">
                      {report.dashboard_status?.sla_days || 7} days
                    </p>
                  </div>
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-bold uppercase text-neutral">Level</p>
                    <p className="mt-1 text-sm font-bold text-charcoal">
                      {report.escalation?.history?.[0]?.escalation_level || 1}
                    </p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}
