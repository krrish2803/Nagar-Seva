'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormEvent, useState } from 'react'

export default function AuthPage() {
  const router = useRouter()
  const [email, setEmail] = useState('citizen_demo@example.com')
  const [password, setPassword] = useState('demo123')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: email,
          password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Invalid email or password')
      }

      localStorage.setItem('nagarseva_token', data.access_token)
      localStorage.setItem(
        'nagarseva_user',
        JSON.stringify({
          userId: data.user_id,
          userType: data.user_type,
          email,
        })
      )

      router.push('/dashboard')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign in. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-civic-light">
      <div className="mx-auto flex min-h-screen max-w-7xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid w-full max-w-5xl grid-cols-1 overflow-hidden rounded-lg bg-white shadow-xl md:grid-cols-[1fr_420px]">
          <section className="bg-gradient-to-br from-civic-dark via-civic to-trust-dark p-8 text-white sm:p-12">
            <Link href="/" className="mb-16 inline-flex items-center space-x-2">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-lg font-bold text-civic">
                NS
              </span>
              <span className="text-xl font-bold">NagarSeva</span>
            </Link>

            <div className="max-w-lg">
              <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-safety-light">
                Secure Citizen Access
              </p>
              <h1 className="mb-6 text-4xl font-bold leading-tight sm:text-5xl">
                Sign in before reporting an issue.
              </h1>
              <p className="text-lg leading-relaxed text-gray-100">
                Your JWT session keeps reports tied to the right citizen account,
                so every complaint can be tracked from submission to resolution.
              </p>
            </div>
          </section>

          <section className="p-8 sm:p-10">
            <h2 className="mb-2 text-3xl font-bold text-charcoal">Login</h2>
            <p className="mb-8 text-neutral">
              Use your registered email and password to continue.
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="mb-2 block text-sm font-semibold text-charcoal">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-charcoal focus:border-civic focus-visible:outline-none"
                  autoComplete="email"
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-2 block text-sm font-semibold text-charcoal">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 text-charcoal focus:border-civic focus-visible:outline-none"
                  autoComplete="current-password"
                  required
                />
              </div>

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-civic px-5 py-3 font-semibold text-white hover:bg-civic-dark disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isLoading ? 'Authenticating...' : 'Authenticate and Open Dashboard'}
              </button>
            </form>

            <div className="mt-6 rounded-lg bg-civic-light p-4 text-sm text-neutral">
              Demo login: <span className="font-semibold text-charcoal">citizen_demo@example.com</span> /{' '}
              <span className="font-semibold text-charcoal">demo123</span>
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}
