import path from 'path'
import type { NextConfig } from 'next'
// __dirname = services/web/

const nextConfig: NextConfig = {
  output: 'standalone',
  // Aponta para a raiz do monorepo para que o build standalone inclua
  // arquivos de libs/ e para que o Next.js não confunda o workspace root.
  outputFileTracingRoot: path.join(__dirname, '../../'),
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL
    if (!backendUrl) return []
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
      },
    ]
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.camara.leg.br',
        pathname: '/internet/deputado/**',
      },
    ],
  },
}

export default nextConfig
