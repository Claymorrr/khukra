import { NextRequest, NextResponse } from "next/server";

function apiCandidates(): string[] {
  const configured = (
    process.env.KHUKRA_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
  return Array.from(new Set([configured, "http://127.0.0.1:8000"]));
}

async function proxy(req: NextRequest, pathSegments: string[]): Promise<NextResponse> {
  const path = pathSegments.join("/");

  const headers = new Headers();
  const auth = req.headers.get("authorization");
  if (auth) headers.set("authorization", auth);
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  let body: BodyInit | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.arrayBuffer();
  }

  let lastError = "";
  const candidates = apiCandidates();
  for (let index = 0; index < candidates.length; index += 1) {
    const apiBase = candidates[index];
    const target = `${apiBase}/api/${path}${req.nextUrl.search}`;
    try {
      const upstream = await fetch(target, {
        method: req.method,
        headers,
        body,
        cache: "no-store",
      });
      if (upstream.status >= 500 && index < candidates.length - 1) {
        lastError = `${apiBase} returned ${upstream.status}`;
        continue;
      }
      const outHeaders = new Headers();
      const upstreamType = upstream.headers.get("content-type");
      if (upstreamType) outHeaders.set("content-type", upstreamType);
      return new NextResponse(upstream.body, {
        status: upstream.status,
        statusText: upstream.statusText,
        headers: outHeaders,
      });
    } catch (err) {
      lastError = err instanceof Error ? err.message : "Proxy request failed";
    }
  }

  return NextResponse.json(
    {
      detail: `Cannot reach Khukra API. Start the backend with .\\scripts\\start-dev.ps1. (${lastError})`,
    },
    { status: 502 },
  );
}

type RouteCtx = { params: Promise<{ path: string[] }> };

export async function GET(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function POST(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PUT(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PATCH(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function DELETE(req: NextRequest, ctx: RouteCtx) {
  const { path } = await ctx.params;
  return proxy(req, path);
}
