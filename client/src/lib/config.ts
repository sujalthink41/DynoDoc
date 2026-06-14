/** Runtime configuration, sourced from Vite env vars (VITE_*). One source of truth. */
// Default to "" → relative URLs (/api/v1/...). In prod the host proxies /api to
// the backend (see netlify _redirects); in dev Vite proxies it (see vite.config).
// Keeping the API same-origin makes the session cookie first-party, which avoids
// third-party-cookie blocking. Set VITE_API_BASE_URL only to force an absolute URL.
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ''

export const API_PREFIX = '/api/v1'

/** Build a full API URL. Feature modules pass short paths like `/me`, `/intake`. */
export const apiUrl = (path: string): string => `${API_BASE_URL}${API_PREFIX}${path}`
