import { NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8001'

export async function GET(request: Request) {
  const url = new URL(request.url)
  const days = url.searchParams.get('days_lookback') || '30'

  try {
    const response = await fetch(
      `${BACKEND_API_BASE_URL}/api/heatmap/analytics/incident-types?days_lookback=${days}`,
      { cache: 'no-store' }
    )
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch {
    return NextResponse.json(
      { detail: 'Backend incident type API is not reachable.' },
      { status: 503 }
    )
  }
}
