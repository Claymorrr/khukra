/** @type {import('next').NextConfig} */
const apiBase =
  process.env.KHUKRA_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: apiBase,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
