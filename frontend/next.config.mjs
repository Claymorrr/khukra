/** @type {import('next').NextConfig} */
const apiBase =
  process.env.KHUKRA_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: apiBase,
  },
  // Avoid stale/missing lucide-react vendor chunks in dev (barrel import tree-shaking).
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  // /api/* is proxied by src/app/api/[...path]/route.ts (more reliable than rewrites for large JSON).
};

export default nextConfig;
