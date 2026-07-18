'use client'

import { useState } from 'react'
import Link from 'next/link'
import { IconMail } from './Icons'

export default function Footer() {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) {
      setSubscribed(true)
      setEmail('')
      setTimeout(() => setSubscribed(false), 3000)
    }
  }

  return (
    <footer className="bg-charcoal text-white pt-40 md:pt-80 pb-16 md:pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12 md:mb-16">
          {/* Brand */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-civic rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">NS</span>
              </div>
              <span className="font-bold text-xl">NagarSeva</span>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Civic Issues. Fixed. Transparently.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Product</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <a href="#features" className="hover:text-white transition-colors duration-200">
                  Features
                </a>
              </li>
              <li>
                <a href="#solution" className="hover:text-white transition-colors duration-200">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-white transition-colors duration-200">
                  FAQ
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Pricing
                </a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Company</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  About Us
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Careers
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Contact
                </a>
              </li>
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Stay Updated</h3>
            <form onSubmit={handleSubscribe} className="space-y-3">
              <div className="relative">
                <input
                  type="email"
                  placeholder="Your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-civic"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-civic hover:bg-civic-dark text-white font-semibold py-2 px-4 rounded-lg active:scale-98 transition-all duration-200 focus-visible:outline-none flex items-center justify-center space-x-2"
              >
                <IconMail size={18} />
                <span>Subscribe</span>
              </button>
              {subscribed && (
                <p className="text-sm text-civic-light">
                  ✓ Thanks for subscribing!
                </p>
              )}
            </form>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-700 my-12 md:my-16"></div>

        {/* Bottom */}
        <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
          <div>
            <p>&copy; 2024 NagarSeva. All rights reserved.</p>
          </div>
          <div className="flex space-x-6 mt-6 md:mt-0">
            <a href="#" className="hover:text-white transition-colors duration-200">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-white transition-colors duration-200">
              Terms of Service
            </a>
            <a href="#" className="hover:text-white transition-colors duration-200">
              Cookie Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
