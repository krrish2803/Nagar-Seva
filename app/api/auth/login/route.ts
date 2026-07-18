import { NextResponse } from 'next/server'

const BACKEND_API_BASE_URL = process.env.BACKEND_API_BASE_URL || 'http://localhost:8000'

function createDemoToken(userId: string, userType: string, email: string) {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const payload = btoa(
    JSON.stringify({
      sub: userId,
      user_type: userType,
      email,
      iat: Math.floor(Date.now() / 1000),
      demo: true,
    })
  )

  return `${header}.${payload}.demo-signature`
}

export async function POST(request: Request) {
  const body = await request.json()

  try {
    const backendResponse = await fetch(`${BACKEND_API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    })

    const data = await backendResponse.json()

    return NextResponse.json(data, { status: backendResponse.status })
  } catch {
    if (body.username === 'citizen_demo@example.com' && body.password === 'demo123') {
      return NextResponse.json({
        access_token: createDemoToken('CITI_DEMO_001', 'citizen', body.username),
        token_type: 'bearer',
        expires_in: 1800,
        user_id: 'CITI_DEMO_001',
        user_type: 'citizen',
      })
    }

    return NextResponse.json(
      { detail: 'Invalid email or password' },
      { status: 401 }
    )
  }
}
