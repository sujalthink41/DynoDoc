/** Runtime configuration, sourced from Vite env vars (VITE_*). */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
