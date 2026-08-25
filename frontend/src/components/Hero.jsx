import "./Hero.css";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import legalHero from "../assets/legal-hero.png";

function Hero() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <section className="law-hero">
      <div className="law-hero-copy">
        <div className="india-badge">
          <span aria-hidden="true">🇮🇳</span>
          <span>LawMate AI</span>
        </div>

        <h1 className="hero-title">
          LawMate <span>AI</span>
        </h1>

        <h2 className="hero-subtitle">{t.heroTagline}</h2>

        <p className="hero-description">{t.home.chatDesc}</p>

        <div className="hero-actions">
          <button className="hero-primary" onClick={() => navigate("/chat")}> 
            <span aria-hidden="true">⚖</span>
            {t.home.ask}
          </button>
          <button className="hero-secondary" onClick={() => navigate("/upload")}> 
            {t.home.upload}
            <span aria-hidden="true">→</span>
          </button>
        </div>
      </div>

      <div className="law-hero-visual" aria-label="Indian legal symbols illustration">
        <img src={legalHero} alt="Indian legal symbols including justice scales, the Supreme Court, Constitution of India and Lady Justice" />
      </div>
    </section>
  );
}

export default Hero;
