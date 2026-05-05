/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://localhost:${process.env.API_PORT || "8001"}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
