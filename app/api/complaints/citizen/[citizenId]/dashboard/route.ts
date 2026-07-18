import { NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8001'

export async function GET(
  request: Request,
  { params }: { params: { citizenId: string } }
) {
  const url = new URL(request.url)
  const limit = url.searchParams.get('limit') || '25'

  try {
    const backendResponse = await fetch(
      `${BACKEND_API_BASE_URL}/api/complaints/citizen/${params.citizenId}/dashboard?limit=${limit}`,
      { cache: 'no-store' }
    )
    const data = await backendResponse.json()

    return NextResponse.json(data, { status: backendResponse.status })
  } catch {
    return NextResponse.json(
      { detail: 'Backend dashboard API is not reachable. Start the FastAPI backend to load real reports.' },
      { status: 503 }
    )
  }
}
