import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppLayout } from '@/app/AppLayout'
import { RequireAuth } from '@/app/RequireAuth'
import { LandingPage } from '@/features/landing/LandingPage'
import { ProfilePage } from '@/features/profile/ProfilePage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />

        {/* Authenticated product (gated + app shell) */}
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route path="/profile" element={<ProfilePage />} />
            {/* Course / learning routes land here next. */}
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
