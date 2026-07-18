'use client'

import {
  IconAlertCircle,
  IconChartBar,
  IconEye,
  IconCamera,
  IconMapPin,
  IconClock,
} from './Icons'

export default function FeaturesSection() {
  const features = [
    {
      icon: IconCamera,
      title: 'Voice + Photo Reporting',
      description: 'Citizens speak in any language, add a photo, and the AI drafts the complaint automatically.',
      accent: 'from-safety to-safety-dark',
    },
    {
      icon: IconEye,
      title: 'AI Trust Scoring',
      description: 'Photo quality, voice clarity, GPS confidence, and OTP verification help filter fake reports.',
      accent: 'from-civic to-civic-dark',
    },
    {
      icon: IconAlertCircle,
      title: 'Smart Classification',
      description: 'NVIDIA-powered analysis identifies potholes, streetlights, leaks, garbage, and severity.',
      accent: 'from-trust to-trust-dark',
    },
    {
      icon: IconMapPin,
      title: 'Authority Routing',
      description: 'Complaints are assigned to the right department and official with SLA-based accountability.',
      accent: 'from-civic to-trust',
    },
    {
      icon: IconChartBar,
      title: 'Risk Heatmaps',
      description: 'Clustered complaint intelligence reveals unsafe civic zones and repeat-problem hotspots.',
      accent: 'from-safety to-civic',
    },
    {
      icon: IconClock,
      title: 'AI Progress Updates',
      description: 'Citizens see simple updates like who owns the issue and how many days remain.',
      accent: 'from-trust to-safety',
    },
  ]

  return (
    <section id="features" className="relative overflow-hidden bg-white px-4 py-28 sm:px-6 lg:px-8">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_8%_20%,rgba(29,158,117,.12),transparent_24rem),radial-gradient(circle_at_92%_70%,rgba(235,104,52,.12),transparent_24rem)]" />

      <div className="mx-auto max-w-7xl">
        <div className="mx-auto mb-16 max-w-3xl text-center">
          <p className="mb-3 text-sm font-black uppercase tracking-[0.24em] text-civic">
            Built Like A Civic AI OS
          </p>
          <h2 className="text-4xl font-black tracking-tight text-charcoal sm:text-5xl">
            Features that make the demo feel production-ready
          </h2>
          <p className="mt-5 text-lg leading-8 text-neutral">
            Every card connects to real backend work: authentication, MongoDB persistence,
            NVIDIA AI, routing, trust scoring, escalation, and dashboards.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, idx) => {
            const Icon = feature.icon

            return (
              <div
                key={feature.title}
                className="group relative overflow-hidden rounded-3xl border border-gray-100 bg-white p-7 shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-civic/10"
              >
                <div className={`absolute -right-12 -top-12 h-32 w-32 rounded-full bg-gradient-to-br ${feature.accent} opacity-10 transition-transform duration-500 group-hover:scale-150`} />
                <div className={`mb-7 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${feature.accent} text-white shadow-lg`}>
                  <Icon size={32} strokeWidth={1.6} />
                </div>
                <div className="mb-3 flex items-center gap-3">
                  <span className="text-xs font-black text-neutral/50">0{idx + 1}</span>
                  <div className="h-px flex-1 bg-gray-100" />
                </div>
                <h3 className="text-xl font-black text-charcoal">{feature.title}</h3>
                <p className="mt-3 leading-7 text-neutral">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
