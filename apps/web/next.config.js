/** @type {import('next').NextConfig} */

// In production docker-compose, the API service is at http://api:8000.
// In local dev, it's at http://localhost:8001.
// Rewrites are baked at build time in standalone mode.
const apiUrl = process.env.API_URL || (process.env.NODE_ENV === "production" ? "http://api:8000" : "http://localhost:8001");

const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
