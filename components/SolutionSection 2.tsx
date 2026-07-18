'use client'

export default function SolutionSection() {
  return (
    <section id="solution" className="py-40 md:py-80 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 items-center">
          {/* Left: Text */}
          <div>
            <h2 className="text-4xl sm:text-5xl font-bold text-charcoal mb-6">
              Our Solution
            </h2>
            <p className="text-lg text-neutral mb-6 leading-relaxed">
              NagarSeva is a transparent civic accountability platform that empowers citizens to report issues and hold authorities accountable.
            </p>
            <ul className="space-y-4 mb-8">
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-civic flex items-center justify-center text-white font-bold text-sm">✓</span>
                <span className="text-charcoal">Report civic issues with photos and GPS location</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-civic flex items-center justify-center text-white font-bold text-sm">✓</span>
                <span className="text-charcoal">Real-time tracking of issue resolution</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-civic flex items-center justify-center text-white font-bold text-sm">✓</span>
                <span className="text-charcoal">Transparent governance and public accountability</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-civic flex items-center justify-center text-white font-bold text-sm">✓</span>
                <span className="text-charcoal">Community engagement and crowdsourced solutions</span>
              </li>
            </ul>
            <button className="bg-civic hover:bg-civic-dark text-white font-semibold py-3 px-8 rounded-lg active:scale-98 transition-all duration-200 focus-visible:outline-none">
              Get Started Today
            </button>
          </div>

          {/* Right: Mockup */}
          <div className="relative hidden md:block">
            <div className="bg-gradient-to-br from-civic-light to-trust-light rounded-lg p-1">
              <div className="bg-white rounded-lg overflow-hidden shadow-xl">
                <div className="bg-gradient-to-r from-civic to-trust h-16 flex items-center px-4">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className="h-6 bg-gray-200 rounded w-4/5"></div>
                  <div className="h-4 bg-gray-200 rounded w-full"></div>
                  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                  <div className="mt-8 h-40 bg-gradient-to-br from-safety-light to-safety rounded-lg opacity-75"></div>
                  <div className="pt-4 space-y-2">
                    <div className="h-3 bg-gray-100 rounded"></div>
                    <div className="h-3 bg-gray-100 rounded w-4/5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
