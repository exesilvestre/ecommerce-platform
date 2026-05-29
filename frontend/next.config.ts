import type { NextConfig } from "next";

function getApiUrl(): string {
  const raw = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!raw) {
    throw new Error(
      "Missing API_URL: set it in Vercel (Settings → Environment Variables) to your backend base URL, e.g. https://your-api.up.railway.app (no trailing slash).",
    );
  }
  return raw.replace(/\/$/, "");
}

const nextConfig: NextConfig = {
  async rewrites() {
    const apiUrl = getApiUrl();
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
