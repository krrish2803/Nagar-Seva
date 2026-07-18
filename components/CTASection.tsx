'use client'

import Link from 'next/link'

export default function CTASection() {
  return (
    <section className="relative overflow-hidden bg-white px-4 py-28 sm:px-6 lg:px-8">
      <div className="absolute left-1/2 top-1/2 h-[34rem] w-[34rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-civic/10 blur-3xl" />

      <div className="relative mx-auto max-w-6xl overflow-hidden rounded-[2.5rem] bg-charcoal p-8 text-center shadow-2xl shadow-charcoal/20 sm:p-12 lg:p-16">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(29,158,117,.42),transparent_26rem),radial-gradient(circle_at_85%_30%,rgba(235,104,52,.35),transparent_24rem),radial-gradient(circle_at_50%_100%,rgba(55,138,221,.28),transparent_28rem)]" />
        <div className="absolute -left-24 -top-24 h-56 w-56 rounded-full border border-white/10" />
        <div className="absolute -bottom-20 -right-20 h-72 w-72 rounded-full border border-white/10" />

        <div className="relative">
          <p className="mb-4 text-sm font-black uppercase tracking-[0.24em] text-civic-light">
            Ready for the demo?
          </p>
          <h2 className="mx-auto max-w-4xl text-4xl font-black tracking-tight text-white sm:text-6xl">
            Let citizens report faster. Let authorities respond smarter.
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-white/70">
            Open the authenticated flow, submit a report, and show judges the full loop:
            AI draft → trust score → routing → dashboard progress.
          </p>

          <div className="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
            <Link
              href="/auth"
              className="rounded-2xl bg-safety px-8 py-4 font-black text-white shadow-xl shadow-safety/25 hover:bg-safety-dark"
            >
              Report an Issue Now
            </Link>
            <Link
              href="/dashboard"
              className="rounded-2xl border border-white/20 bg-white/10 px-8 py-4 font-black text-white backdrop-blur hover:bg-white/20"
            >
              View Citizen Dashboard
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
