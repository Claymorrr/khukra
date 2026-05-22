/**
 * API root for fetch calls.
 * In the browser we use same-origin `/api` so Next.js rewrites proxy to the backend
 * (avoids CORS NetworkError from localhost:3000 → 127.0.0.1:8000).
 */
export function resolveApiRoot(): string {
  if (typeof window !== "undefined") {
    return "/api";
  }
  const direct = (
    process.env.KHUKRA_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    ""
  ).replace(/\/$/, "");
  if (direct) return `${direct}/api`;
  return "/api";
}
