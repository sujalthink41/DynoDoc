/** Mirrors the backend `UserProfile` DTO (GET /api/v1/me). */
export interface UserProfile {
  id: string
  email: string
  display_name: string | null
  avatar_url: string | null
  is_active: boolean
}
