import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Thin proxy so the browser only ever talks to the Next.js origin. Forwards
 * multipart uploads to the FastAPI backend, which hands dataset storage off
 * to S3 (via signed URLs) and kicks off the AgentCore pipeline.
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    const upstream = await fetch(`${API_BASE_URL}/api/v1/datasets/upload`, {
      method: "POST",
      body: formData,
    });

    if (!upstream.ok) {
      return NextResponse.json(
        { error: "Upload failed", status: upstream.status },
        { status: upstream.status }
      );
    }

    const data = await upstream.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: "Could not reach the DataSpot backend." },
      { status: 502 }
    );
  }
}
