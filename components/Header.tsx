'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-white/20 bg-white/80 shadow-sm backdrop-blur-xl">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link href="#" className="flex items-center space-x-2 focus-visible:outline-none">
          <div className="w-10 h-10 bg-gradient-to-br from-civic to-trust rounded-xl flex items-center justify-center shadow-lg shadow-civic/20">
            <span className="text-white font-bold text-lg">NS</span>
          </div>
          <span className="font-bold text-xl text-charcoal hidden sm:inline">NagarSeva</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <a href="#problem" className="text-neutral hover:text-charcoal transition-colors duration-200 focus-visible:outline-none">
            Problem
          </a>
          <a href="#solution" className="text-neutral hover:text-charcoal transition-colors duration-200 focus-visible:outline-none">
            Solution
          </a>
          <a href="#features" className="text-neutral hover:text-charcoal transition-colors duration-200 focus-visible:outline-none">
            Features
          </a>
          <a href="#how-it-works" className="text-neutral hover:text-charcoal transition-colors duration-200 focus-visible:outline-none">
            How It Works
          </a>
          <a href="#faq" className="text-neutral hover:text-charcoal transition-colors duration-200 focus-visible:outline-none">
            FAQ
          </a>
        </div>

        {/* Report Now CTA */}
        <Link href="/auth" className="bg-gradient-to-r from-civic to-trust hover:from-civic-dark hover:to-trust-dark text-white font-semibold py-2.5 px-4 sm:px-6 rounded-xl shadow-lg shadow-civic/20 focus-visible:outline-none active:scale-98 transition-all duration-200">
          Report Now
        </Link>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden ml-4 p-2 rounded-lg hover:bg-gray-100 focus-visible:outline-none"
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
      </nav>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 py-4 space-y-4">
            <a href="#problem" className="block text-neutral hover:text-charcoal transition-colors duration-200">
              Problem
            </a>
            <a href="#solution" className="block text-neutral hover:text-charcoal transition-colors duration-200">
              Solution
            </a>
            <a href="#features" className="block text-neutral hover:text-charcoal transition-colors duration-200">
              Features
            </a>
            <a href="#how-it-works" className="block text-neutral hover:text-charcoal transition-colors duration-200">
              How It Works
            </a>
            <a href="#faq" className="block text-neutral hover:text-charcoal transition-colors duration-200">
              FAQ
            </a>
          </div>
        </div>
      )}
    </header>
  )
}
