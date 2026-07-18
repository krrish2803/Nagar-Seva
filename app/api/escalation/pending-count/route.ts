import { NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8001'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/api/escalation/pending-count`, {
      cache: 'no-store',
    })
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch {
    return NextResponse.json(
      { detail: 'Backend escalation API is not reachable.' },
      { status: 503 }
    )
  }
}
