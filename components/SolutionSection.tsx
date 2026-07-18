'use client'

import Link from 'next/link'

export default function SolutionSection() {
  const points = [
    'Voice-first reporting for citizens who prefer speaking over typing',
    'AI classification, trust scoring, and complaint drafting in one flow',
    'MongoDB-backed complaint history, status, escalation, and dashboard tracking',
    'Authority routing with SLA visibility for real municipal accountability',
  ]

  return (
    <section id="solution" className="relative overflow-hidden bg-civic-light px-4 py-28 sm:px-6 lg:px-8">
      <div className="absolute right-0 top-0 h-80 w-80 rounded-full bg-trust/10 blur-3xl" />
      <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-2">
        <div>
          <p className="mb-3 text-sm font-black uppercase tracking-[0.24em] text-civic">
            The Solution
          </p>
          <h2 className="text-4xl font-black tracking-tight text-charcoal sm:text-5xl">
            A transparent bridge between citizens and municipal teams
          </h2>
          <p className="mt-5 text-lg leading-8 text-neutral">
            NagarSeva is not just a complaint form. It is an AI-assisted workflow
            that verifies evidence, understands the issue, routes it, and keeps the citizen informed.
          </p>

          <div className="mt-8 space-y-4">
            {points.map((point) => (
              <div key={point} className="flex gap-4 rounded-2xl bg-white/70 p-4 shadow-sm backdrop-blur">
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-civic text-sm font-black text-white">
                  ✓
                </span>
                <span className="font-semibold leading-7 text-charcoal">{point}</span>
              </div>
            ))}
          </div>

          <Link
            href="/auth"
            className="mt-8 inline-flex rounded-2xl bg-charcoal px-7 py-4 font-bold text-white shadow-xl shadow-charcoal/20 hover:bg-civic-dark"
          >
            Open Secure Dashboard
          </Link>
        </div>

        <div className="relative mx-auto w-full max-w-xl [perspective:1200px]">
          <div className="float-3d rounded-[2rem] bg-gradient-to-br from-civic via-trust to-safety p-1 shadow-2xl shadow-trust/20 [transform:rotateX(9deg)_rotateY(10deg)]">
            <div className="rounded-[1.85rem] bg-white p-5">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-xs font-black uppercase tracking-wide text-civic">Citizen Dashboard</p>
                  <h3 className="text-2xl font-black text-charcoal">My Reports</h3>
                </div>
                <div className="rounded-full bg-civic-light px-3 py-1 text-xs font-bold text-civic">JWT secured</div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                {[
                  ['12', 'Total'],
                  ['04', 'Active'],
                  ['02', 'Escalated'],
                ].map(([value, label]) => (
                  <div key={label} className="rounded-2xl bg-gray-50 p-4 text-center">
                    <p className="text-2xl font-black text-charcoal">{value}</p>
                    <p className="text-xs font-bold text-neutral">{label}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 space-y-3">
                {[
                  ['Broken streetlight', 'With electrician · 4 days left', 'bg-safety'],
                  ['Water leak', 'Assigned to water works', 'bg-trust'],
                  ['Garbage pile', 'Resolved yesterday', 'bg-civic'],
                ].map(([title, status, color]) => (
                  <div key={title} className="flex items-center gap-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
                    <span className={`h-12 w-12 rounded-2xl ${color}`} />
                    <div className="min-w-0 flex-1">
                      <p className="font-black text-charcoal">{title}</p>
                      <p className="text-sm font-semibold text-neutral">{status}</p>
                    </div>
                    <span className="h-2.5 w-2.5 rounded-full bg-green-400" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
