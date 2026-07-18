'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'

type AppSidebarProps = {
  userEmail?: string
  userType?: string
  userId?: string
}

export default function AppSidebar({ userEmail, userType, userId }: AppSidebarProps) {
  const pathname = usePathname()
  const router = useRouter()

  const navItems = [
    {
      href: '/dashboard',
      label: 'Citizen Dashboard',
      description: 'Reports, AI trust score, upload access',
    },
    {
      href: '/upload',
      label: 'Upload',
      description: 'Submit photo, voice, and report PDF',
    },
    {
      href: '/classification',
      label: 'AI Classification',
      description: 'Issue type, severity, AI confidence',
    },
    {
      href: '/routing',
      label: 'Authority Routing',
      description: 'Department, official, SLA assignment',
    },
    {
      href: '/escalation',
      label: 'Escalation',
      description: 'Overdue reports and escalation levels',
    },
    {
      href: '/heatmap',
      label: 'Heatmap Analytics',
      description: 'Risk clusters and incident patterns',
    },
  ]

  const handleSignOut = () => {
    localStorage.removeItem('nagarseva_token')
    localStorage.removeItem('nagarseva_user')
    router.push('/')
  }

  return (
    <aside className="z-40 flex w-full flex-col border-b border-gray-200 bg-white p-4 shadow-sm lg:sticky lg:top-0 lg:h-screen lg:w-[320px] lg:min-w-[320px] lg:max-w-[320px] lg:shrink-0 lg:border-b-0 lg:border-r lg:p-5">
      <Link href="/" className="mb-5 flex items-center space-x-3 lg:mb-8">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-civic to-trust text-lg font-bold text-white">
          NS
        </span>
        <div>
          <p className="text-xl font-black text-charcoal">NagarSeva</p>
          <p className="text-xs font-semibold text-neutral">Citizen Console</p>
        </div>
      </Link>

      <nav className="grid gap-2 sm:grid-cols-2 lg:block lg:space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-2xl p-4 transition-all ${
                isActive
                  ? 'bg-civic text-white shadow-lg shadow-civic/20'
                  : 'bg-gray-50 text-charcoal hover:bg-civic-light'
              }`}
            >
              <span className="block text-base font-bold leading-tight">{item.label}</span>
              <span className={`mt-1 hidden text-xs leading-5 sm:block ${isActive ? 'text-white/75' : 'text-neutral'}`}>
                {item.description}
              </span>
            </Link>
          )
        })}
      </nav>

      <div className="mt-5 rounded-2xl bg-civic-light p-4 lg:mt-auto">
        <p className="text-xs font-bold uppercase tracking-wide text-civic">Signed In</p>
        <p className="mt-2 break-words text-sm font-bold text-charcoal">{userEmail || 'Citizen'}</p>
        <p className="mt-1 text-xs capitalize text-neutral">
          {userType || 'citizen'} · {userId || 'active session'}
        </p>
        <button
          onClick={handleSignOut}
          className="mt-4 w-full rounded-xl border border-civic px-4 py-2 text-sm font-bold text-civic hover:bg-civic hover:text-white"
        >
          Sign Out
        </button>
      </div>
    </aside>
  )
}
