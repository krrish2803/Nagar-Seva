import Header from '@/components/Header'
import HeroSection from '@/components/HeroSection'
import ProblemStatement from '@/components/ProblemStatement'
import SolutionSection from '@/components/SolutionSection'
import USPSection from '@/components/USPSection'
import FeaturesSection from '@/components/FeaturesSection'
import HowItWorks from '@/components/HowItWorks'
import ImpactSection from '@/components/ImpactSection'
import FAQSection from '@/components/FAQSection'
import CTASection from '@/components/CTASection'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <main>
      <Header />
      <HeroSection />
      <ProblemStatement />
      <SolutionSection />
      <USPSection />
      <FeaturesSection />
      <HowItWorks />
      <ImpactSection />
      <FAQSection />
      <CTASection />
      <Footer />
    </main>
  )
}
