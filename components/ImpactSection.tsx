'use client'

export default function ImpactSection() {
  const stats = [
    {
      value: '50K+',
      label: 'Issues Reported',
      subtext: 'And counting across cities',
    },
    {
      value: '78%',
      label: 'Resolution Rate',
      subtext: 'Within 30 days of reporting',
    },
    {
      value: '2M+',
      label: 'Community Members',
      subtext: 'Making cities better together',
    },
  ]

  return (
    <section className="relative overflow-hidden py-28 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-civic to-civic-dark">
      <div className="absolute inset-0 opacity-20 [background-image:radial-gradient(circle_at_center,white_1px,transparent_1px)] [background-size:34px_34px]" />
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <p className="mb-3 text-sm font-black uppercase tracking-[0.24em] text-civic-light">
            Demo metrics
          </p>
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
            Impact authorities can understand instantly
          </h2>
          <p className="text-lg text-gray-100 max-w-2xl mx-auto">
            Transforming cities through transparency and accountability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="relative overflow-hidden rounded-3xl border border-white/20 bg-white/10 p-8 text-center shadow-2xl shadow-black/10 backdrop-blur transition-all duration-300 hover:-translate-y-2 hover:bg-white/20 md:p-12"
            >
              <div className="text-5xl md:text-6xl font-bold text-white mb-3">
                {stat.value}
              </div>
              <div className="text-xl md:text-2xl font-semibold text-gray-100 mb-2">
                {stat.label}
              </div>
              <div className="text-gray-300 text-sm">
                {stat.subtext}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
