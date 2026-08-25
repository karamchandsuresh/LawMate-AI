import "./Hero.css";
import { useLanguage } from "../context/LanguageContext";

function Hero() {
  const { t } = useLanguage();
  return (
    <>
      <h1 className="hero-title">⚖️ LawMate AI</h1>
      <p className="hero-description">{t.heroTagline}</p>
    </>
  );
}
export default Hero;
