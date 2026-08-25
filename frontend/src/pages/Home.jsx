import "./Home.css";

import Hero from "../components/Hero";
import FeatureCard from "../components/FeatureCard";
import InfoSection from "../components/InfoSection";
import { useLanguage } from "../context/LanguageContext";

function Home() {
  const { t } = useLanguage();

  return (
    <div className="home-page">
      <Hero />

      <InfoSection />

      <section className="home-features-section">
        <div className="features">
          <FeatureCard
            icon="💬"
            accent="blue"
            title={t.home.chatTitle}
            description={t.home.chatDesc}
          />

          <FeatureCard
            icon="📄"
            accent="green"
            title={t.home.docTitle}
            description={t.home.docDesc}
          />

          <FeatureCard
            icon="✍"
            accent="purple"
            title={t.home.complaintTitle}
            description={t.home.complaintDesc}
          />

          <FeatureCard
            icon="🛡"
            accent="orange"
            title={t.home.caseTitle}
            description={t.home.caseDesc}
          />
        </div>
      </section>
    </div>
  );
}

export default Home;
