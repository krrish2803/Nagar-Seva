const FALLBACK_RENDER_BACKEND_URL = 'https://nagar-seva-q2oe.onrender.com'

export function getBackendUrl() {
  const configuredBackendUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL

  if (configuredBackendUrl) {
    return configuredBackendUrl.replace(/\/$/, '')
  }

  if (typeof window !== 'undefined' && window.location.hostname.endsWith('netlify.app')) {
    return FALLBACK_RENDER_BACKEND_URL
  }

  return ''
}

export function apiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${getBackendUrl()}${normalizedPath}`
}
