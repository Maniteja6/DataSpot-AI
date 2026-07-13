import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// No authentication in this prototype — DataSpot AI is fully open on load.
// Kept as a pass-through so request-level concerns (headers, locale) can be
// added later without restructuring routes.
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [],
};
