import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  images: {
    domains: ["www.gravatar.com"], // ✅ fixes Avatar initials bug
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*", // proxy to FastAPI
      },
    ];
  },
};

export default nextConfig;
