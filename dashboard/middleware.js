import { NextResponse } from "next/server";

export function middleware(request) {
  const password = process.env.DASHBOARD_PASSWORD;
  if (!password) {
    return new NextResponse("Dashboard authentication is not configured.", { status: 503 });
  }

  const authorization = request.headers.get("authorization") || "";
  if (authorization.startsWith("Basic ")) {
    try {
      const decoded = atob(authorization.slice(6));
      const separator = decoded.indexOf(":");
      const suppliedPassword = separator >= 0 ? decoded.slice(separator + 1) : "";
      if (suppliedPassword === password) return NextResponse.next();
    } catch {
      // Invalid Basic Auth header; challenge below.
    }
  }

  return new NextResponse("الدخول خاص بصاحب لوحة التحكم.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Quran Studio Dashboard", charset="UTF-8"' }
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
