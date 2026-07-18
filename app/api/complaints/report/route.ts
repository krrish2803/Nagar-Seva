import { NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8001'

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    const backendResponse = await fetch(`${BACKEND_API_BASE_URL}/api/complaints/report`, {
      method: 'POST',
      body: formData,
      cache: 'no-store',
    })
    const data = await backendResponse.json()

    return NextResponse.json(data, { status: backendResponse.status })
  } catch {
    return NextResponse.json(
      { detail: 'Backend complaint API is not reachable. Start the FastAPI backend before uploading a report.' },
      { status: 503 }
    )
  }
}
