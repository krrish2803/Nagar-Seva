'use client'

import Link from 'next/link'

export default function HeroSection() {
  return (
    <section className="relative bg-gradient-to-br from-civic-dark via-civic to-trust-dark overflow-hidden pt-80 pb-80 md:pt-80 md:pb-80">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full -mr-48 -mt-48"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white rounded-full -ml-48 -mb-48"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 items-center">
          {/* Left: Text Content */}
          <div className="z-10">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
              Civic Issues.
              <br />
              <span className="text-safety-light">Fixed.</span>
              <br />
              Transparently.
            </h1>
            <p className="text-lg text-gray-100 mb-8 max-w-md">
              Report potholes, broken streetlights, and civic problems in your city. Track resolution in real-time and hold authorities accountable.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/auth" className="bg-safety hover:bg-safety-dark text-white font-semibold py-3 px-8 rounded-lg text-center active:scale-98 transition-all duration-200 focus-visible:outline-none">
                Report an Issue Now
              </Link>
              <button className="bg-white hover:bg-gray-100 text-civic font-semibold py-3 px-8 rounded-lg border-2 border-white active:scale-98 transition-all duration-200 focus-visible:outline-none">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Right: App Interface Mockup */}
          <div className="relative hidden md:block">
            {/* Phone Frame */}
            <div className="mx-auto max-w-sm">
              <div className="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-105 transition-transform duration-300 border-8 border-gray-900">
                {/* Phone Notch */}
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-40 h-7 bg-gray-900 rounded-b-3xl z-10"></div>
                
                {/* Phone Content */}
                <div className="bg-gradient-to-b from-civic-light to-white min-h-screen pt-8">
                  {/* Header */}
                  <div className="px-6 pb-4">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-xl font-bold text-charcoal">Report Issue</h2>
                      <div className="w-8 h-8 rounded-full bg-safety flex items-center justify-center text-white text-xs font-bold">✓</div>
                    </div>
                  </div>

                  {/* Issue Card - Pothole */}
                  <div className="px-6 pb-4">
                    <div className="bg-white rounded-2xl overflow-hidden shadow-md border border-gray-100">
                      {/* Image Placeholder */}
                      <div className="h-48 bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center">
                        <div className="text-4xl">🕳️</div>
                      </div>
                      
                      {/* Issue Details */}
                      <div className="p-4 space-y-3">
                        <div>
                          <p className="text-xs font-semibold text-neutral uppercase">Issue Type</p>
                          <p className="text-sm font-bold text-charcoal">Large Pothole - Road Hazard</p>
                        </div>
                        
                        <div>
                          <p className="text-xs font-semibold text-neutral uppercase">Location</p>
                          <p className="text-sm text-charcoal">Main Street, Ward 7</p>
                        </div>

                        <div className="flex items-center space-x-2">
                          <span className="inline-block px-2 py-1 bg-safety-light text-safety text-xs font-bold rounded">HIGH PRIORITY</span>
                          <span className="inline-block px-2 py-1 bg-civic-light text-civic text-xs font-bold rounded">REPORTED</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Status Timeline */}
                  <div className="px-6 pb-4">
                    <p className="text-xs font-semibold text-neutral uppercase mb-3">Status Timeline</p>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full bg-civic flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">✓</div>
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-charcoal">Reported</p>
                          <p className="text-xs text-neutral">2 min ago</p>
                        </div>
                      </div>
                      
                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full bg-trust flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">✓</div>
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-charcoal">Routed to PWD</p>
                          <p className="text-xs text-neutral">1 min ago</p>
                        </div>
                      </div>

                      <div className="flex items-start space-x-3">
                        <div className="w-6 h-6 rounded-full border-2 border-gray-300 flex-shrink-0 mt-0.5"></div>
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-neutral">In Progress</p>
                          <p className="text-xs text-neutral">Estimated 3 days</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <div className="px-6 pb-6">
                    <button className="w-full bg-civic hover:bg-civic-dark text-white font-semibold py-2 rounded-lg text-sm">
                      Track Progress
                    </button>
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
