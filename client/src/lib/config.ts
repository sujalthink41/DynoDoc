/** Runtime configuration, sourced from Vite env vars (VITE_*). One source of truth. */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const API_PREFIX = '/api/v1'

/** Build a full API URL. Feature modules pass short paths like `/me`, `/intake`. */
export const apiUrl = (path: string): string => `${API_BASE_URL}${API_PREFIX}${path}`
