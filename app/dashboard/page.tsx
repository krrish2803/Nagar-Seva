'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import AppSidebar from '@/components/AppSidebar'
import { generateIssuePdf } from '@/lib/reportPdf'
import type { PdfReportData } from '@/lib/reportPdf'

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
  created_at?: string
  location?: {
    latitude?: number
    longitude?: number
    address?: string
    ward_id?: string
    pin_code?: string
  }
  classification?: {
    issue_type?: string
    severity?: string
    recommended_department?: string
  }
  assignment?: {
    official_name?: string
    official_role?: string
    department?: string
    sla_days?: number
  }
  photos?: string[]
  media_attachments?: Array<{
    type?: string
    url?: string
    file_name?: string
  }>
  ai_progress_update?: string
  dashboard_status?: {
    sla_days?: number
    days_remaining?: number
    is_overdue?: boolean
  }
  escalation?: {
    is_escalated?: boolean
    latest_status?: string
    history?: Array<{
      _id?: string
      escalation_level?: number
      status?: string
      created_at?: string
    }>
  }
  trust_summary?: {
    score?: number
    action?: string
    flags?: string[]
    otp_verified?: boolean
  }
}

type DashboardData = {
  citizen_id: string
  total_reports: number
  active_reports: number
  resolved_reports: number
  escalated_reports: number
  reports: Report[]
}

const statusStyles: Record<string, string> = {
  submitted: 'bg-blue-50 text-blue-700 ring-blue-200',
  classified: 'bg-purple-50 text-purple-700 ring-purple-200',
  assigned: 'bg-amber-50 text-amber-700 ring-amber-200',
  in_progress: 'bg-civic/10 text-civic ring-civic/20',
  resolved: 'bg-green-50 text-green-700 ring-green-200',
}

function formatLabel(value?: string) {
  return value ? value.replace(/_/g, ' ') : 'Not available'
}

function getReportId(report: Report) {
  return report._id || report.id || 'Pending ID'
}

function getReportPhotos(report: Report) {
  if (report.photos?.length) {
    return report.photos
  }

  return (
    report.media_attachments
      ?.filter((attachment) => attachment.type === 'image' && attachment.url)
      .map((attachment) => attachment.url as string) || []
  )
}

function formatDate(value?: string) {
  if (!value) {
    return 'Recently'
  }

  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function getUploadedImageName(report: Report) {
  const imageAttachment = report.media_attachments?.find(
    (attachment) => attachment.type === 'image'
  )
  if (imageAttachment?.file_name) {
    return imageAttachment.file_name
  }
  if (imageAttachment?.url) {
    return imageAttachment.url.split('/').pop() || imageAttachment.url
  }
  return 'No image uploaded'
}

function createPdfDataFromReport(report: Report): PdfReportData {
  return {
    issue_title: report.issue_title || '',
    issue_description: report.issue_description || '',
    address: report.location?.address || '',
    latitude: report.location?.latitude?.toString() || '',
    longitude: report.location?.longitude?.toString() || '',
    ward_id: report.location?.ward_id || '',
    pin_code: report.location?.pin_code || '',
    uploaded_image_name: getUploadedImageName(report),
    complaint_id: getReportId(report),
  }
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<StoredUser | null>(null)
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [isLoadingReports, setIsLoadingReports] = useState(false)
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
        loadDashboard(parsedUser.userId)
      }
    } catch {
      localStorage.removeItem('nagarseva_token')
      localStorage.removeItem('nagarseva_user')
      router.replace('/auth')
      return
    }

    setIsCheckingSession(false)
  }, [router])

  const loadDashboard = async (citizenId: string) => {
    setIsLoadingReports(true)
    setError('')

    try {
      const response = await fetch(
        `/api/complaints/citizen/${citizenId}/dashboard?limit=25`,
        { cache: 'no-store' }
      )
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to load dashboard')
      }

      setDashboard(data)
    } catch (loadError) {
      setDashboard({
        citizen_id: citizenId,
        total_reports: 0,
        active_reports: 0,
        resolved_reports: 0,
        escalated_reports: 0,
        reports: [],
      })
      setError(loadError instanceof Error ? loadError.message : 'Unable to load reports')
    } finally {
      setIsLoadingReports(false)
    }
  }

  const latestReport = useMemo(() => dashboard?.reports?.[0], [dashboard])



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
        <div className="mb-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-civic">
              Citizen Dashboard
            </p>
            <h1 className="text-4xl font-bold text-charcoal">
              My Reports
            </h1>
            <p className="mt-3 max-w-2xl text-neutral">
              Track every complaint, see AI-generated progress updates, review evidence,
              and know when a report has been escalated.
            </p>
          </div>

          <aside className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
            <p className="text-sm font-semibold uppercase text-neutral">Signed in as</p>
            <p className="mt-2 break-words text-lg font-bold text-charcoal">{user?.email}</p>
            <p className="mt-1 text-sm capitalize text-neutral">{user?.userType} · {user?.userId}</p>
          </aside>
        </div>

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            ['Total Reports', dashboard?.total_reports ?? 0],
            ['Active', dashboard?.active_reports ?? 0],
            ['Resolved', dashboard?.resolved_reports ?? 0],
            ['Escalated', dashboard?.escalated_reports ?? 0],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-100">
              <p className="text-sm font-semibold text-neutral">{label}</p>
              <p className="mt-2 text-3xl font-bold text-charcoal">{value}</p>
            </div>
          ))}
        </div>

        {latestReport && (
          <section className="mt-8 rounded-3xl bg-gradient-to-r from-civic to-civic-dark p-6 text-white shadow-lg">
            <p className="text-sm font-semibold uppercase text-white/80">Latest AI Update</p>
            <h2 className="mt-2 text-2xl font-bold">{latestReport.issue_title}</h2>
            <p className="mt-3 max-w-3xl text-lg text-white/90">
              {latestReport.ai_progress_update}
            </p>
          </section>
        )}

        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_360px]">
          <section className="space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-charcoal">Report History</h2>
              {isLoadingReports && <span className="text-sm font-semibold text-civic">Refreshing...</span>}
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
                {error}
              </div>
            )}

            {!isLoadingReports && dashboard?.reports?.length === 0 && (
              <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
                <h3 className="text-xl font-bold text-charcoal">No reports yet</h3>
                <p className="mt-2 text-neutral">
                  Click Upload Report to create your first complaint.
                </p>
              </div>
            )}

            {dashboard?.reports?.map((report) => {
              const status = report.status || 'submitted'
              const photos = getReportPhotos(report)
              const statusClass = statusStyles[status] || 'bg-gray-50 text-gray-700 ring-gray-200'

              return (
                <article key={getReportId(report)} className="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-gray-100">
                  <div className="grid gap-0 md:grid-cols-[220px_1fr]">
                    <div className="min-h-52 bg-gray-100">
                      {photos[0] ? (
                        <img
                          src={photos[0]}
                          alt={`${report.issue_title || 'Complaint'} evidence`}
                          className="h-full min-h-52 w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full min-h-52 items-center justify-center bg-civic/10 px-6 text-center text-sm font-semibold text-civic">
                          No photo attached
                        </div>
                      )}
                    </div>

                    <div className="p-6">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wide text-neutral">
                            {getReportId(report)} · {formatDate(report.created_at)}
                          </p>
                          <h3 className="mt-2 text-2xl font-bold text-charcoal">
                            {report.issue_title || 'Civic issue'}
                          </h3>
                          <p className="mt-2 text-sm text-neutral">
                            {report.location?.address || 'Location not available'}
                          </p>
                        </div>

                        <span className={`rounded-full px-3 py-1 text-xs font-bold capitalize ring-1 ${statusClass}`}>
                          {formatLabel(status)}
                        </span>
                      </div>

                      <p className="mt-4 rounded-2xl bg-civic-light p-4 text-sm font-semibold text-charcoal">
                        {report.ai_progress_update || 'AI progress update is being prepared.'}
                      </p>

                      <div className="mt-5 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-xl bg-gray-50 p-3">
                          <p className="text-xs font-semibold uppercase text-neutral">Assigned To</p>
                          <p className="mt-1 text-sm font-bold text-charcoal">
                            {report.assignment?.official_role || report.assignment?.official_name || report.assignment?.department || 'Municipal team'}
                          </p>
                        </div>
                        <div className="rounded-xl bg-gray-50 p-3">
                          <p className="text-xs font-semibold uppercase text-neutral">Trust Score</p>
                          <p className="mt-1 text-sm font-bold text-charcoal">
                            {Math.round((report.trust_summary?.score || 0) * 100)}%
                            {report.trust_summary?.otp_verified ? ' · OTP verified' : ''}
                          </p>
                        </div>
                        <div className="rounded-xl bg-gray-50 p-3">
                          <p className="text-xs font-semibold uppercase text-neutral">SLA</p>
                          <p className="mt-1 text-sm font-bold text-charcoal">
                            {report.dashboard_status?.is_overdue
                              ? 'Overdue'
                              : `${report.dashboard_status?.days_remaining ?? 0} days left`}
                          </p>
                        </div>
                      </div>

                      <div className="mt-4 flex flex-wrap gap-2">
                        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold capitalize text-neutral">
                          {formatLabel(report.classification?.issue_type)}
                        </span>
                        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold capitalize text-neutral">
                          {formatLabel(report.classification?.severity)} severity
                        </span>
                        {report.escalation?.is_escalated && (
                          <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700">
                            Escalated · {formatLabel(report.escalation.latest_status)}
                          </span>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={() => generateIssuePdf(createPdfDataFromReport(report))}
                        className="mt-5 rounded-xl border border-civic bg-white px-4 py-2 text-sm font-bold text-civic hover:bg-civic hover:text-white"
                      >
                        Generate PDF Report
                      </button>
                    </div>
                  </div>
                </article>
              )
            })}
          </section>

          <aside className="space-y-5">
            <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
              <h2 className="text-xl font-bold text-charcoal">Upload New Report</h2>
              <p className="mt-2 text-sm text-neutral">
                Open the dedicated upload page to submit details, photo evidence, and an optional voice note.
              </p>
              <Link
                href="/upload"
                className="mt-5 inline-flex w-full items-center justify-center rounded-xl bg-safety px-5 py-3 font-semibold text-white hover:bg-safety-dark"
              >
                Upload Report
              </Link>
            </section>

            <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
              <h2 className="text-xl font-bold text-charcoal">Escalation Status</h2>
              <div className="mt-4 space-y-3">
                {dashboard?.reports
                  ?.filter((report) => report.escalation?.is_escalated)
                  .slice(0, 3)
                  .map((report) => (
                    <div key={`${getReportId(report)}-escalation`} className="rounded-2xl bg-red-50 p-4">
                      <p className="font-bold text-red-800">{report.issue_title}</p>
                      <p className="mt-1 text-sm text-red-700">
                        {formatLabel(report.escalation?.latest_status)} · Level{' '}
                        {report.escalation?.history?.[0]?.escalation_level || 1}
                      </p>
                    </div>
                  ))}
                {!dashboard?.reports?.some((report) => report.escalation?.is_escalated) && (
                  <p className="rounded-2xl bg-green-50 p-4 text-sm font-semibold text-green-700">
                    No active escalations. Nice and calm — the way dashboards should be.
                  </p>
                )}
              </div>
            </section>
          </aside>
        </div>
      </section>
    </main>
  )
}
