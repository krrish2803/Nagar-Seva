'use client'

import { IconTrophy, IconMapPin, IconCamera } from './Icons'

export default function USPSection() {
  const features = [
    {
      icon: IconCamera,
      title: 'Photo Evidence',
      description: 'Attach photos and GPS location to create an irrefutable record of civic issues.',
      color: 'safety',
    },
    {
      icon: IconMapPin,
      title: 'Live Map Tracking',
      description: 'View all reported issues on an interactive map and track their status in real-time.',
      color: 'trust',
    },
    {
      icon: IconTrophy,
      title: 'Impact Rewards',
      description: 'Citizens earn badges and recognition for contributing to civic improvements.',
      color: 'civic',
    },
  ]

  return (
    <section className="py-28 px-4 sm:px-6 lg:px-8 bg-charcoal text-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <p className="mb-3 text-sm font-black uppercase tracking-[0.24em] text-civic-light">
            Judge-friendly differentiation
          </p>
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
            Why NagarSeva stands out
          </h2>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Voice-first access, verified evidence, and visible accountability — tuned for real Indian civic usage.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon
            const bgColors = {
              safety: 'bg-white/10 border border-white/10 hover:border-safety/50',
              trust: 'bg-white/10 border border-white/10 hover:border-trust/50',
              civic: 'bg-white/10 border border-white/10 hover:border-civic/50',
            }
            const textColors = {
              safety: 'text-safety',
              trust: 'text-trust',
              civic: 'text-civic',
            }

            return (
              <div
                key={idx}
                className={`p-8 rounded-3xl backdrop-blur transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-black/20 ${bgColors[feature.color as keyof typeof bgColors]}`}
              >
                <div className={`w-14 h-14 rounded-2xl bg-white flex items-center justify-center mb-6 ${textColors[feature.color as keyof typeof textColors]}`}>
                  <Icon size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-black text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-white/70 text-base leading-7">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
