'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import AppSidebar from '@/components/AppSidebar'
import { generateIssuePdf } from '@/lib/reportPdf'
import type { ChangeEvent, FormEvent } from 'react'
import type { PdfReportData } from '@/lib/reportPdf'

type StoredUser = {
  userId: string
  userType: string
  email: string
}

type ReportFormState = {
  issue_title: string
  issue_description: string
  address: string
  ward_id: string
  pin_code: string
  latitude: string
  longitude: string
}

export default function UploadPage() {
  const router = useRouter()
  const [user, setUser] = useState<StoredUser | null>(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [isSubmittingReport, setIsSubmittingReport] = useState(false)
  const [submitMessage, setSubmitMessage] = useState('')
  const [lastUploadedPdfData, setLastUploadedPdfData] = useState<PdfReportData | null>(null)
  const [reportForm, setReportForm] = useState<ReportFormState>({
    issue_title: '',
    issue_description: '',
    address: '',
    ward_id: '',
    pin_code: '',
    latitude: '28.6139',
    longitude: '77.2090',
  })
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [audioFile, setAudioFile] = useState<File | null>(null)

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

  const handleReportFormChange = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = event.target
    setReportForm((current) => ({ ...current, [name]: value }))
  }

  const handleSubmitReport = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!user?.userId) {
      setSubmitMessage('Please sign in again before submitting a report.')
      return
    }

    setIsSubmittingReport(true)
    setSubmitMessage('')
    setLastUploadedPdfData(null)

    const formData = new FormData()
    formData.append('citizen_id', user.userId)
    formData.append('issue_title', reportForm.issue_title)
    formData.append('issue_description', reportForm.issue_description)
    formData.append('address', reportForm.address)
    formData.append('latitude', reportForm.latitude)
    formData.append('longitude', reportForm.longitude)
    if (reportForm.ward_id) {
      formData.append('ward_id', reportForm.ward_id)
    }
    if (reportForm.pin_code) {
      formData.append('pin_code', reportForm.pin_code)
    }
    if (photoFile) {
      formData.append('image_file', photoFile)
    }
    if (audioFile) {
      formData.append('audio_file', audioFile)
    }

    try {
      const response = await fetch('/api/complaints/report', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to submit report')
      }

      const pdfData = {
        issue_title: reportForm.issue_title,
        issue_description: reportForm.issue_description,
        address: reportForm.address,
        latitude: reportForm.latitude,
        longitude: reportForm.longitude,
        ward_id: reportForm.ward_id,
        pin_code: reportForm.pin_code,
        uploaded_image_name: photoFile?.name || 'No image uploaded',
        complaint_id: data.complaint_id,
      }

      setSubmitMessage(`Report uploaded successfully: ${data.complaint_id}`)
      setLastUploadedPdfData(pdfData)
    } catch (submitError) {
      setSubmitMessage(
        submitError instanceof Error ? submitError.message : 'Unable to submit report'
      )
    } finally {
      setIsSubmittingReport(false)
    }
  }

  const handleResetForm = () => {
    setReportForm({
      issue_title: '',
      issue_description: '',
      address: '',
      ward_id: '',
      pin_code: '',
      latitude: reportForm.latitude,
      longitude: reportForm.longitude,
    })
    setPhotoFile(null)
    setAudioFile(null)
    setSubmitMessage('')
    setLastUploadedPdfData(null)
  }

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
            Upload Report
          </p>
          <h1 className="text-4xl font-bold text-charcoal">
            Submit a civic issue
          </h1>
          <p className="mt-3 max-w-2xl text-neutral">
            Upload the issue details, image evidence, and optional voice note. After upload,
            generate a premium PDF report for download or printing.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <form onSubmit={handleSubmitReport} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
            <div className="grid gap-5 md:grid-cols-2">
              <label className="block md:col-span-2">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Issue Title
                </span>
                <input
                  required
                  name="issue_title"
                  value={reportForm.issue_title}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                  placeholder="Broken streetlight near main gate"
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Description
                </span>
                <textarea
                  required
                  name="issue_description"
                  value={reportForm.issue_description}
                  onChange={handleReportFormChange}
                  className="min-h-32 w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                  placeholder="Describe the issue, exact location, and safety risk."
                />
              </label>

              <label className="block md:col-span-2">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Address
                </span>
                <input
                  required
                  name="address"
                  value={reportForm.address}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                  placeholder="Sector 18 Market Road, Near Metro Gate 2, Noida"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Latitude
                </span>
                <input
                  required
                  name="latitude"
                  type="number"
                  step="any"
                  value={reportForm.latitude}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Longitude
                </span>
                <input
                  required
                  name="longitude"
                  type="number"
                  step="any"
                  value={reportForm.longitude}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  Ward
                </span>
                <input
                  name="ward_id"
                  value={reportForm.ward_id}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                  placeholder="ward_012"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-charcoal">
                  PIN
                </span>
                <input
                  name="pin_code"
                  value={reportForm.pin_code}
                  onChange={handleReportFormChange}
                  className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-civic focus-visible:outline-none"
                  placeholder="201301"
                />
              </label>

              <label className="block rounded-2xl border-2 border-dashed border-civic/30 bg-civic-light p-5 text-center">
                <span className="block text-sm font-bold text-civic">Upload Photo</span>
                <span className="mt-1 block text-xs text-neutral">
                  {photoFile ? photoFile.name : 'Choose image evidence'}
                </span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(event) => setPhotoFile(event.target.files?.[0] || null)}
                  className="sr-only"
                />
              </label>

              <label className="block rounded-2xl border-2 border-dashed border-safety/30 bg-safety-light p-5 text-center">
                <span className="block text-sm font-bold text-safety">Upload Voice Note</span>
                <span className="mt-1 block text-xs text-neutral">
                  {audioFile ? audioFile.name : 'Optional audio complaint'}
                </span>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(event) => setAudioFile(event.target.files?.[0] || null)}
                  className="sr-only"
                />
              </label>
            </div>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <button
                type="submit"
                disabled={isSubmittingReport}
                className="flex-1 rounded-xl bg-safety px-5 py-3 font-semibold text-white hover:bg-safety-dark disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSubmittingReport ? 'Uploading...' : 'Upload Report'}
              </button>
              <button
                type="button"
                onClick={handleResetForm}
                className="rounded-xl border border-gray-300 px-5 py-3 font-semibold text-charcoal hover:border-civic hover:text-civic"
              >
                Clear
              </button>
            </div>
          </form>

          <aside className="space-y-5">
            <section className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
              <h2 className="text-xl font-bold text-charcoal">Upload Status</h2>
              <p className="mt-2 text-sm text-neutral">
                Signed in as {user?.email}. Your report will be saved to MongoDB and shown on the dashboard.
              </p>

              {submitMessage && (
                <p className="mt-5 rounded-xl bg-gray-50 p-3 text-sm font-semibold text-charcoal">
                  {submitMessage}
                </p>
              )}

              {lastUploadedPdfData && (
                <div className="mt-5 space-y-3">
                  <button
                    type="button"
                    onClick={() => generateIssuePdf(lastUploadedPdfData)}
                    className="w-full rounded-xl border border-civic bg-civic-light px-5 py-3 font-semibold text-civic hover:bg-civic hover:text-white"
                  >
                    Generate Report PDF
                  </button>
                  <Link
                    href="/dashboard"
                    className="inline-flex w-full items-center justify-center rounded-xl bg-charcoal px-5 py-3 font-semibold text-white hover:bg-civic-dark"
                  >
                    View Dashboard
                  </Link>
                </div>
              )}
            </section>

            <section className="rounded-3xl bg-charcoal p-6 text-white shadow-sm">
              <h2 className="text-xl font-bold">PDF Flow</h2>
              <p className="mt-2 text-sm text-white/70">
                After upload succeeds, click Generate Report PDF. A premium report opens in a new print window; choose Save as PDF.
              </p>
            </section>
          </aside>
        </div>
      </section>
    </main>
  )
}
