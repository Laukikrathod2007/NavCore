/** @type {import('next').NextConfig} */
const isGitHubPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  reactStrictMode: true,
  ...(isGitHubPages
    ? {
        output: "export",
        basePath: "/NavCore",
        trailingSlash: true,
      }
    : {
        // Keep the local development proxy; production builds use the configured API URL.
        async rewrites() {
          return [
            {
              source: "/api/:path*",
              destination: "http://localhost:8001/:path*",
            },
          ];
        },
      }),
};

module.exports = nextConfig;
