import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NagarSeva - Civic Issues. Fixed. Transparently.',
  description: 'Report civic issues in your city and track their resolution transparently. Empower your community with accountability.',
  keywords: ['civic accountability', 'community safety', 'transparent governance', 'city issues'],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#0F6E56" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
