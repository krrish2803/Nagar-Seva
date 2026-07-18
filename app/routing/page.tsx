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
  issue_description?: string
  status?: string
  location?: {
    address?: string
    ward_id?: string
  }
  classification?: {
    issue_type?: string
    severity?: string
    recommended_department?: string
  }
  assignment?: {
    official_id?: string
    official_name?: string
    official_role?: string
    department?: string
    sla_days?: number
  }
  dashboard_status?: {
    days_remaining?: number
    is_overdue?: boolean
    sla_days?: number
  }
  escalation?: {
    is_escalated?: boolean
    latest_status?: string
  }
}

type DashboardData = {
  reports: Report[]
}

function formatLabel(value?: string) {
  return value ? value.replace(/_/g, ' ') : 'Not available'
}

function getReportId(report: Report) {
  return report._id || report.id || 'Pending ID'
}

export default function RoutingPage() {
  const router = useRouter()
  const [user, setUser] = useState<StoredUser | null>(null)
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
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

    async function loadReports() {
      setIsLoading(true)
      setError('')

      try {
        const response = await fetch(
          `/api/complaints/citizen/${user?.userId}/dashboard?limit=25`,
          { cache: 'no-store' }
        )
        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.detail || 'Unable to load routing assignments')
        }

        setDashboard(data)
      } catch (loadError) {
        setDashboard({ reports: [] })
        setError(loadError instanceof Error ? loadError.message : 'Unable to load routing assignments')
      } finally {
        setIsLoading(false)
      }
    }

    loadReports()
  }, [user?.userId])

  const reports = useMemo(() => dashboard?.reports || [], [dashboard])

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
            Authority Routing
          </p>
          <h1 className="text-4xl font-bold text-charcoal">
            Department and SLA assignment
          </h1>
          <p className="mt-3 max-w-3xl text-neutral">
            This page shows the authority routing output created after upload: department,
            assigned official, official role, SLA, and escalation state.
          </p>
        </div>

        {error && (
          <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="mb-5 flex items-center justify-between rounded-3xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
          <div>
            <h2 className="text-xl font-bold text-charcoal">Routing Queue</h2>
            <p className="mt-1 text-sm text-neutral">
              {isLoading ? 'Loading authority assignments...' : `${reports.length} routed reports found`}
            </p>
          </div>
          <Link
            href="/upload"
            className="rounded-xl bg-safety px-5 py-3 font-semibold text-white hover:bg-safety-dark"
          >
            Upload Report
          </Link>
        </div>

        {reports.length === 0 && !isLoading && (
          <div className="rounded-3xl bg-white p-8 text-center shadow-sm ring-1 ring-gray-100">
            <h3 className="text-2xl font-bold text-charcoal">No routing yet</h3>
            <p className="mx-auto mt-2 max-w-xl text-neutral">
              Upload a complaint first. Once routed, assignment details appear here.
            </p>
          </div>
        )}

        <div className="space-y-5">
          {reports.map((report) => {
            const assignment = report.assignment || {}
            const classification = report.classification || {}
            const dashboardStatus = report.dashboard_status || {}

            return (
              <article key={getReportId(report)} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
                <div className="grid gap-6 lg:grid-cols-[1.2fr_.8fr]">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-neutral">
                      {getReportId(report)}
                    </p>
                    <h2 className="mt-2 text-2xl font-bold text-charcoal">
                      {report.issue_title || 'Civic issue'}
                    </h2>
                    <p className="mt-2 text-sm text-neutral">
                      {report.location?.address || 'Location not available'}
                    </p>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      <div className="rounded-2xl bg-civic-light p-4">
                        <p className="text-xs font-bold uppercase text-civic">Department</p>
                        <p className="mt-1 text-lg font-black text-charcoal">
                          {formatLabel(assignment.department || classification.recommended_department)}
                        </p>
                      </div>
                      <div className="rounded-2xl bg-trust-light p-4">
                        <p className="text-xs font-bold uppercase text-trust">Assigned Official</p>
                        <p className="mt-1 text-lg font-black text-charcoal">
                          {assignment.official_name || assignment.official_role || 'Municipal team'}
                        </p>
                      </div>
                      <div className="rounded-2xl bg-safety-light p-4">
                        <p className="text-xs font-bold uppercase text-safety">SLA</p>
                        <p className="mt-1 text-lg font-black text-charcoal">
                          {assignment.sla_days || dashboardStatus.sla_days || 7} days
                        </p>
                      </div>
                      <div className="rounded-2xl bg-gray-50 p-4">
                        <p className="text-xs font-bold uppercase text-neutral">Time Left</p>
                        <p className="mt-1 text-lg font-black text-charcoal">
                          {dashboardStatus.is_overdue
                            ? 'Overdue'
                            : `${dashboardStatus.days_remaining ?? 0} days left`}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl bg-charcoal p-5 text-white">
                    <p className="text-xs font-bold uppercase text-civic-light">Routing Decision</p>
                    <p className="mt-3 text-sm leading-6 text-white/75">
                      The router matched this {formatLabel(classification.issue_type)} complaint to{' '}
                      {formatLabel(assignment.department || classification.recommended_department)} based on issue type,
                      ward, severity, and available official workload.
                    </p>
                    <dl className="mt-5 space-y-3 text-sm">
                      <div>
                        <dt className="font-bold text-white/60">Official ID</dt>
                        <dd className="text-white">{assignment.official_id || 'Not available'}</dd>
                      </div>
                      <div>
                        <dt className="font-bold text-white/60">Ward</dt>
                        <dd className="text-white">{report.location?.ward_id || 'Not available'}</dd>
                      </div>
                      <div>
                        <dt className="font-bold text-white/60">Escalation</dt>
                        <dd className="capitalize text-white">
                          {report.escalation?.is_escalated
                            ? formatLabel(report.escalation.latest_status)
                            : 'Not escalated'}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}
