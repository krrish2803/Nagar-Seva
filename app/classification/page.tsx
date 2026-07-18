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
  classification?: {
    issue_type?: string
    severity?: string
    confidence?: number
    recommended_department?: string
    keywords?: string[]
    description?: string
  }
  trust_summary?: {
    score?: number
    action?: string
    flags?: string[]
    otp_verified?: boolean
  }
  photos?: string[]
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

export default function ClassificationPage() {
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
          throw new Error(data.detail || 'Unable to load classifications')
        }

        setDashboard(data)
      } catch (loadError) {
        setDashboard({ reports: [] })
        setError(loadError instanceof Error ? loadError.message : 'Unable to load classifications')
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
            AI Classification
          </p>
          <h1 className="text-4xl font-bold text-charcoal">
            Issue intelligence results
          </h1>
          <p className="mt-3 max-w-3xl text-neutral">
            This page uses saved complaint records after upload. The backend classification agent
            detects issue type, severity, confidence, recommended department, and trust quality.
          </p>
        </div>

        {error && (
          <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="mb-5 flex items-center justify-between rounded-3xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
          <div>
            <h2 className="text-xl font-bold text-charcoal">Classification Queue</h2>
            <p className="mt-1 text-sm text-neutral">
              {isLoading ? 'Loading AI classifications...' : `${reports.length} classified reports found`}
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
            <h3 className="text-2xl font-bold text-charcoal">No classification yet</h3>
            <p className="mx-auto mt-2 max-w-xl text-neutral">
              Upload a report first. After the backend classifies it, the result appears here.
            </p>
          </div>
        )}

        <div className="grid gap-5 xl:grid-cols-2">
          {reports.map((report) => {
            const classification = report.classification || {}
            const trust = report.trust_summary || {}

            return (
              <article key={getReportId(report)} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-neutral">
                      {getReportId(report)}
                    </p>
                    <h2 className="mt-2 text-2xl font-bold text-charcoal">
                      {report.issue_title || 'Civic issue'}
                    </h2>
                  </div>
                  <span className="rounded-full bg-civic-light px-3 py-1 text-xs font-bold capitalize text-civic">
                    {formatLabel(report.status)}
                  </span>
                </div>

                <p className="mt-4 text-sm leading-6 text-neutral">
                  {report.issue_description || 'No description provided'}
                </p>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-2xl bg-civic-light p-4">
                    <p className="text-xs font-bold uppercase text-civic">Issue Type</p>
                    <p className="mt-1 text-lg font-black capitalize text-charcoal">
                      {formatLabel(classification.issue_type)}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-safety-light p-4">
                    <p className="text-xs font-bold uppercase text-safety">Severity</p>
                    <p className="mt-1 text-lg font-black capitalize text-charcoal">
                      {formatLabel(classification.severity)}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-trust-light p-4">
                    <p className="text-xs font-bold uppercase text-trust">Trust Score</p>
                    <p className="mt-1 text-lg font-black text-charcoal">
                      {Math.round((trust.score || 0) * 100)}%
                    </p>
                  </div>
                </div>

                <div className="mt-5 rounded-2xl bg-gray-50 p-4">
                  <p className="text-xs font-bold uppercase text-neutral">AI Summary</p>
                  <p className="mt-2 text-sm leading-6 text-charcoal">
                    {classification.description ||
                      `Classified as ${formatLabel(classification.issue_type)} with ${formatLabel(classification.severity)} severity.`}
                  </p>
                  <p className="mt-3 text-sm font-semibold text-neutral">
                    Recommended department: {formatLabel(classification.recommended_department)}
                  </p>
                  <p className="mt-1 text-sm font-semibold text-neutral">
                    Trust action: {formatLabel(trust.action)}
                  </p>
                </div>
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}
