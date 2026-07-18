'use client'

import { useState } from 'react'
import { IconChevronDown } from './Icons'

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const faqs = [
    {
      question: 'How do I report a civic issue?',
      answer: 'Simply open the NagarSeva app, take a photo of the issue, add details about location and problem type, and submit. The issue will immediately appear on our map and be assigned to relevant authorities.',
    },
    {
      question: 'Is it really free to use?',
      answer: 'Yes, NagarSeva is completely free for citizens. We believe civic accountability should be accessible to everyone. Government agencies pay for premium features.',
    },
    {
      question: 'How long does it take to resolve an issue?',
      answer: 'Resolution times vary by issue type and location. Our data shows 78% of issues are resolved within 30 days. You can track progress in real-time on the app.',
    },
    {
      question: 'What happens after I report an issue?',
      answer: 'Your report is verified by our team, assigned to the relevant municipal department, and added to the public map. Authorities must provide updates, and you receive notifications throughout the resolution process.',
    },
    {
      question: 'Can I remain anonymous?',
      answer: 'You can report issues with an optional anonymous profile. However, we recommend providing contact information so authorities can reach you for clarifications.',
    },
    {
      question: 'What types of issues can I report?',
      answer: 'You can report potholes, broken streetlights, water leaks, waste accumulation, damaged sidewalks, missing manhole covers, and most civic infrastructure issues.',
    },
    {
      question: 'How is my data protected?',
      answer: 'We follow strict data protection protocols compliant with GDPR and national privacy laws. Your personal information is never shared with third parties without consent.',
    },
    {
      question: 'Can I suggest a feature?',
      answer: 'Absolutely! We\'d love your feedback. You can suggest features directly through the app settings or email our team at feedback@nagarseva.com.',
    },
  ]

  const toggleAccordion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section id="faq" className="py-40 md:py-80 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-16 md:mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-charcoal mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-neutral">
            Everything you need to know about NagarSeva.
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="border border-gray-200 rounded-lg overflow-hidden hover:border-civic transition-colors duration-200"
            >
              <button
                onClick={() => toggleAccordion(idx)}
                className="w-full px-6 py-4 md:py-5 flex items-center justify-between text-left focus-visible:outline-none focus-visible:bg-civic-light"
                aria-expanded={openIndex === idx}
              >
                <span className="text-lg font-semibold text-charcoal pr-4">
                  {faq.question}
                </span>
                <IconChevronDown
                  size={24}
                  className={`flex-shrink-0 text-civic transition-transform duration-300 ${
                    openIndex === idx ? 'transform rotate-180' : ''
                  }`}
                />
              </button>

              {openIndex === idx && (
                <div className="px-6 py-4 md:py-5 bg-gray-50 border-t border-gray-200 accordion-enter">
                  <p className="text-neutral leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
