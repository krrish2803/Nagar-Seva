/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendApiBaseUrl = process.env.BACKEND_API_BASE_URL || 'http://localhost:8001'

    return [
      {
        source: '/uploads/:path*',
        destination: `${backendApiBaseUrl}/uploads/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
