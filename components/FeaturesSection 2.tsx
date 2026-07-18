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
      icon: IconAlertCircle,
      title: 'Quick Report',
      description: 'Report issues in seconds with our simple, intuitive mobile app.',
    },
    {
      icon: IconChartBar,
      title: 'Analytics Dashboard',
      description: 'View comprehensive statistics and trends of civic issues in your area.',
    },
    {
      icon: IconEye,
      title: 'Live Visibility',
      description: 'Government agencies provide real-time updates on issue resolution.',
    },
    {
      icon: IconCamera,
      title: 'Photo Proof',
      description: 'Attach multiple photos and GPS data to substantiate your reports.',
    },
    {
      icon: IconMapPin,
      title: 'Location Tracking',
      description: 'See all reported issues on an interactive city map.',
    },
    {
      icon: IconClock,
      title: 'Resolution Timeline',
      description: 'Track the complete history and timeline of each issue\'s resolution.',
    },
  ]

  return (
    <section id="features" className="py-40 md:py-80 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-charcoal mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-neutral max-w-2xl mx-auto">
            Everything you need to make your city better, one issue at a time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-32 md:gap-24">
          {features.map((feature, idx) => {
            const Icon = feature.icon

            return (
              <div key={idx} className="group">
                <div className="w-16 h-16 rounded-lg bg-civic-light flex items-center justify-center mb-6 group-hover:bg-civic group-hover:text-white transition-all duration-200 text-civic">
                  <Icon size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-bold text-charcoal mb-3">
                  {feature.title}
                </h3>
                <p className="text-neutral text-base leading-relaxed">
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
