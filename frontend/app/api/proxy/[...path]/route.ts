import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Generic pass-through proxy for GET/POST/PUT/DELETE to the FastAPI backend.
 * Lets the frontend call same-origin `/api/proxy/*` paths in environments
 * (like some Vercel preview setups) where direct cross-origin calls to the
 * AWS-hosted backend are restricted.
 */
async function forward(request: NextRequest, path: string[]) {
  const targetUrl = `${API_BASE_URL}/${path.join("/")}${request.nextUrl.search}`;

  const upstream = await fetch(targetUrl, {
    method: request.method,
    headers: { "Content-Type": "application/json" },
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
  });

  const data = await upstream.text();
  return new NextResponse(data, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("Content-Type") ?? "application/json" },
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: RouteContext) {
  return forward(request, (await context.params).path);
}
export async function POST(request: NextRequest, context: RouteContext) {
  return forward(request, (await context.params).path);
}
export async function PUT(request: NextRequest, context: RouteContext) {
  return forward(request, (await context.params).path);
}
export async function DELETE(request: NextRequest, context: RouteContext) {
  return forward(request, (await context.params).path);
}
