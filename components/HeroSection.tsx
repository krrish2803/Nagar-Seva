'use client'

import Link from 'next/link'

export default function HeroSection() {
  return (
    <section id="report" className="relative isolate overflow-hidden bg-charcoal pt-28 text-white sm:pt-32 lg:pt-36">
      <div className="absolute inset-0 -z-20 bg-[radial-gradient(circle_at_18%_18%,rgba(29,158,117,0.42),transparent_28rem),radial-gradient(circle_at_82%_10%,rgba(55,138,221,0.38),transparent_30rem),linear-gradient(135deg,#10251f_0%,#102d46_50%,#2c2c2a_100%)]" />
      <div className="absolute inset-0 -z-10 opacity-25 [background-image:linear-gradient(rgba(255,255,255,.08)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.08)_1px,transparent_1px)] [background-size:72px_72px]" />
      <div className="absolute left-1/2 top-28 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-safety/20 blur-3xl" />

      <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 pb-24 sm:px-6 lg:grid-cols-[1.02fr_.98fr] lg:px-8 lg:pb-32">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-civic-light backdrop-blur">
            <span className="h-2 w-2 rounded-full bg-safety pulse-glow" />
            AI civic reporting for Indian cities
          </div>

          <h1 className="max-w-4xl text-5xl font-black leading-[0.96] tracking-tight sm:text-6xl lg:text-7xl">
            Report civic issues.
            <span className="block bg-gradient-to-r from-civic-light via-white to-safety-light bg-clip-text text-transparent">
              Let AI route the fix.
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-white/80">
            NagarSeva turns voice notes, photos, GPS, trust scoring, and authority routing
            into one transparent complaint journey citizens can actually follow.
          </p>

          <div className="mt-9 flex flex-col gap-4 sm:flex-row">
            <Link
              href="/auth"
              className="group relative overflow-hidden rounded-2xl bg-safety px-7 py-4 text-center font-bold text-white shadow-2xl shadow-safety/30 hover:bg-safety-dark"
            >
              <span className="relative z-10">Report an Issue Now</span>
              <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/25 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            </Link>
            <Link
              href="#features"
              className="rounded-2xl border border-white/20 bg-white/10 px-7 py-4 text-center font-bold text-white backdrop-blur hover:bg-white/20"
            >
              Explore AI Features
            </Link>
          </div>

          <div className="mt-10 grid max-w-xl grid-cols-3 gap-3">
            {[
              ['Voice-first', 'Any language'],
              ['Trust score', 'Fake-proof reports'],
              ['Live SLA', 'Progress updates'],
            ].map(([title, label]) => (
              <div key={title} className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
                <p className="text-sm font-black text-white">{title}</p>
                <p className="mt-1 text-xs font-semibold text-white/60">{label}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-xl [perspective:1400px]">
          <div className="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-civic/30" />
          <div className="orbit-dot absolute left-1/2 top-1/2 h-4 w-4 rounded-full bg-safety shadow-lg shadow-safety/50" />

          <div className="float-3d relative rounded-[2rem] border border-white/20 bg-white/10 p-4 shadow-2xl shadow-black/30 backdrop-blur-xl [transform:rotateX(8deg)_rotateY(-13deg)]">
            <div className="rounded-[1.5rem] bg-white p-4 text-charcoal shadow-2xl">
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-civic">Live AI Desk</p>
                  <p className="text-lg font-black">Complaint Routed</p>
                </div>
                <div className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">87% trusted</div>
              </div>

              <div className="mt-5 grid gap-4 sm:grid-cols-[1fr_.72fr]">
                <div className="space-y-3">
                  <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-civic-light to-trust-light p-4 shine-sweep">
                    <div className="mb-12 h-24 rounded-xl bg-gradient-to-br from-charcoal to-trust-dark opacity-90" />
                    <div className="absolute left-7 top-10 h-7 w-7 rounded-full border-4 border-white bg-safety shadow-lg" />
                    <p className="text-xs font-bold uppercase text-neutral">Photo + GPS detected</p>
                    <p className="mt-1 font-black">Broken streetlight near school</p>
                  </div>

                  <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-safety text-lg text-white">🎙️</div>
                      <div>
                        <p className="text-sm font-black">Voice translated</p>
                        <p className="text-xs text-neutral">Hindi → English draft ready</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    ['Classified', 'Streetlight', 'bg-civic-light text-civic'],
                    ['Assigned', 'Electrician', 'bg-trust-light text-trust'],
                    ['SLA', '4 days', 'bg-safety-light text-safety'],
                  ].map(([label, value, classes]) => (
                    <div key={label} className={`rounded-2xl p-4 ${classes}`}>
                      <p className="text-xs font-bold uppercase opacity-70">{label}</p>
                      <p className="mt-1 text-lg font-black">{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 rounded-2xl bg-charcoal p-4 text-white">
                <p className="text-xs font-bold uppercase text-civic-light">Citizen update</p>
                <p className="mt-2 text-sm font-semibold text-white/80">
                  Your streetlight complaint is with the electrician — expected resolution in 4 days.
                </p>
              </div>
            </div>
          </div>

          <div className="float-3d-slow absolute -bottom-8 -left-4 hidden rounded-3xl border border-white/20 bg-white/10 p-4 text-white shadow-xl backdrop-blur md:block">
            <p className="text-xs font-bold uppercase text-civic-light">Heatmap alert</p>
            <p className="text-2xl font-black">12</p>
            <p className="text-xs text-white/70">high-risk reports nearby</p>
          </div>
        </div>
      </div>
    </section>
  )
}
