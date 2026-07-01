/** @type {import('next').NextConfig} */
const apiBase =
  process.env.KHUKRA_LOGISTICS_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8010";

const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: apiBase,
  },
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
};

export default nextConfig;
