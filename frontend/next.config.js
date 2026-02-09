/** @type {import('next').NextConfig} */

const isTauri = process.env.TAURI_ENV_PLATFORM !== undefined;

// Get the API URL for server-side rewrites
const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  // Use localhost for server-side since Next.js server and backend are on same machine
  return 'http://localhost:8000';
};

const nextConfig = {
  reactStrictMode: true,
  output: isTauri ? 'export' : undefined,
  // Allow any hostname in development
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', '192.168.1.20:3000'],
    },
  },
  images: {
    unoptimized: isTauri,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
  async rewrites() {
    if (isTauri) return [];
    return [
      {
        source: '/api/:path*',
        destination: `${getApiUrl()}/api/:path*`,
      },
      {
        source: '/uploads/:path*',
        destination: `${getApiUrl()}/uploads/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
