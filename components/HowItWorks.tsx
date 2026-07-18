'use client'

import { IconCamera, IconMapPin, IconChartBar, IconEye, IconCheck } from './Icons'

export default function HowItWorks() {
  const steps = [
    {
      icon: IconCamera,
      title: 'Report',
      description: 'Take a photo of the civic issue and submit it with details.',
    },
    {
      icon: IconMapPin,
      title: 'Locate',
      description: 'The issue is pinned to the map for authorities to see.',
    },
    {
      icon: IconChartBar,
      title: 'Track',
      description: 'Authorities assign the issue and begin working on it.',
    },
    {
      icon: IconEye,
      title: 'Monitor',
      description: 'Track real-time progress and updates from authorities.',
    },
    {
      icon: IconCheck,
      title: 'Verify',
      description: 'Confirm resolution and rate the authority\'s response.',
    },
  ]

  return (
    <section id="how-it-works" className="py-40 md:py-80 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-charcoal mb-4">
            How It Works
          </h2>
          <p className="text-lg text-neutral max-w-2xl mx-auto">
            Five simple steps to make your city better.
          </p>
        </div>

        {/* Desktop: Horizontal Flow */}
        <div className="hidden md:block">
          <div className="flex items-stretch justify-between gap-4 relative">
            {/* Connecting Line */}
            <div className="absolute top-1/4 left-0 right-0 h-1 bg-gradient-to-r from-civic via-trust to-safety -z-10 transform translate-y-8"></div>

            {steps.map((step, idx) => {
              const Icon = step.icon
              return (
                <div key={idx} className="flex-1 text-center">
                  <div className="w-20 h-20 rounded-full bg-white border-4 border-civic flex items-center justify-center mx-auto mb-6 text-civic relative z-10">
                    <Icon size={40} strokeWidth={1.5} />
                  </div>
                  <h3 className="text-xl font-bold text-charcoal mb-2">
                    {step.title}
                  </h3>
                  <p className="text-neutral text-sm">
                    {step.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Mobile: Vertical Flow */}
        <div className="md:hidden space-y-8">
          {steps.map((step, idx) => {
            const Icon = step.icon
            return (
              <div key={idx} className="flex items-start space-x-6">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-16 w-16 rounded-full bg-civic text-white">
                    <Icon size={32} strokeWidth={1.5} />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-charcoal mb-1">
                    {step.title}
                  </h3>
                  <p className="text-neutral text-sm">
                    {step.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
