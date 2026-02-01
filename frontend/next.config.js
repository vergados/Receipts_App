/** @type {import('next').NextConfig} */

const isTauri = process.env.TAURI_ENV_PLATFORM !== undefined;

const nextConfig = {
  reactStrictMode: true,
  output: isTauri ? 'export' : undefined,
  images: {
    unoptimized: isTauri,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  async rewrites() {
    if (isTauri) return [];
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
