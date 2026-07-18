'use client'

import { IconAlertCircle, IconEye, IconClock } from './Icons'

export default function ProblemStatement() {
  const problems = [
    {
      icon: IconAlertCircle,
      title: 'Civic Issues Ignored',
      description: 'Potholes, broken lights, and waste accumulation go unreported and unresolved for months.',
      color: 'safety',
    },
    {
      icon: IconEye,
      title: 'Lack of Visibility',
      description: 'Citizens have no way to track if their complaints are being addressed or who is responsible.',
      color: 'trust',
    },
    {
      icon: IconClock,
      title: 'No Accountability',
      description: 'Government agencies operate without transparency. There\'s no public tracking of issue resolution.',
      color: 'civic',
    },
  ]

  return (
    <section id="problem" className="relative overflow-hidden py-28 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-civic/30 to-transparent" />
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <p className="mb-3 text-sm font-black uppercase tracking-[0.24em] text-safety">
            Civic friction
          </p>
          <h2 className="text-4xl sm:text-5xl font-black text-charcoal mb-4">
            Why complaints disappear
          </h2>
          <p className="text-lg text-neutral max-w-2xl mx-auto">
            Cities face broken systems, silent citizens, and zero accountability for civic issues.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {problems.map((problem, idx) => {
            const Icon = problem.icon
            const colorClasses = {
              safety: 'text-safety bg-safety-light',
              trust: 'text-trust bg-trust-light',
              civic: 'text-civic bg-civic-light',
            }
            const color = colorClasses[problem.color as keyof typeof colorClasses]

            return (
              <div key={idx} className="group rounded-3xl border border-gray-100 bg-white p-8 text-center shadow-sm transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-safety/10">
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-all duration-300 group-hover:scale-110 ${color}`}>
                  <Icon size={32} strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-bold text-charcoal mb-3">
                  {problem.title}
                </h3>
                <p className="text-neutral text-base leading-relaxed">
                  {problem.description}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
