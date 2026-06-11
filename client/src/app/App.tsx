import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppLayout } from '@/app/AppLayout'
import { RequireAuth } from '@/app/RequireAuth'
import { CoursePage } from '@/features/courses/pages/CoursePage'
import { DashboardPage } from '@/features/courses/pages/DashboardPage'
import { IntakePage } from '@/features/courses/pages/IntakePage'
import { LecturePage } from '@/features/courses/pages/LecturePage'
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
            <Route path="/app" element={<DashboardPage />} />
            <Route path="/learn" element={<IntakePage />} />
            <Route path="/courses/:courseId" element={<CoursePage />} />
            <Route path="/lectures/:lectureId" element={<LecturePage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
