/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow large audio uploads (Whisper recordings can be 10-20MB for long takes)
  experimental: {
    serverActions: {
      bodySizeLimit: "25mb",
    },
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8001/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
