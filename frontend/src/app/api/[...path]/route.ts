import { NextRequest, NextResponse } from "next/server";

function apiBase(): string {
  return (
    process.env.KHUKRA_LOGISTICS_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://127.0.0.1:8010"
  ).replace(/\/$/, "");
}

async function proxy(req: NextRequest, pathSegments: string[]): Promise<NextResponse> {
  const path = pathSegments.join("/");
  const headers = new Headers();
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  let body: BodyInit | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.arrayBuffer();
  }

  const target = `${apiBase()}/api/${path}${req.nextUrl.search}`;
  try {
    const upstream = await fetch(target, {
      method: req.method,
      headers,
      body,
      cache: "no-store",
    });
    const outHeaders = new Headers();
    const upstreamType = upstream.headers.get("content-type");
    if (upstreamType) outHeaders.set("content-type", upstreamType);
    return new NextResponse(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: outHeaders,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Proxy failed";
    return NextResponse.json(
      {
        detail: `Cannot reach Khukra Logistics API. Run .\\scripts\\start-dev.ps1. (${msg})`,
      },
      { status: 502 },
    );
  }
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
