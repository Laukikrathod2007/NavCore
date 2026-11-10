const apiBase = (process.env.NEXT_PUBLIC_NAVCORE_API_URL || "").replace(/\/$/, "");
const publicBase = (process.env.NEXT_PUBLIC_BASE_PATH || "").replace(/\/$/, "");

/** Resolve an API path for the Railway deployment or the local Next.js proxy. */
export function apiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return apiBase ? `${apiBase}${normalizedPath}` : `/api${normalizedPath}`;
}

/** Prefix public assets when the site is hosted under a GitHub Pages project path. */
export function publicAsset(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${publicBase}${normalizedPath}`;
}
