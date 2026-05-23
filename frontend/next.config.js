/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://ai-trading-agent-0ujw.onrender.com/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
