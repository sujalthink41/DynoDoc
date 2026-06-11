import { AuroraBackground } from '@/features/landing/components/AuroraBackground'
import { Features } from '@/features/landing/components/Features'
import { FinalCTA } from '@/features/landing/components/FinalCTA'
import { Footer } from '@/features/landing/components/Footer'
import { Hero } from '@/features/landing/components/Hero'
import { HowItWorks } from '@/features/landing/components/HowItWorks'
import { Navbar } from '@/features/landing/components/Navbar'

export function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-x-clip">
      <AuroraBackground />
      <Navbar />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  )
}
