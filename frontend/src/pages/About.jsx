import { useLanguage } from "../context/LanguageContext";
import { featureTranslations } from "../context/featureTranslations";
import "./About.css";

function About() {
  const { language } = useLanguage();
  const text = featureTranslations[language]?.about || featureTranslations.en.about;

  return (
    <div className="about-page">
      <h1>{text.title}</h1>

      <p className="about-intro">{text.intro}</p>

      <section className="about-section">
        <h2>{text.missionTitle}</h2>
        <p>{text.missionText}</p>
      </section>

      <section className="about-section">
        <h2>{text.featuresTitle}</h2>
        <ul>
          {text.features.map((feature) => (
            <li key={feature}>{feature}</li>
          ))}
        </ul>
      </section>

      <section className="about-section">
        <h2>{text.techTitle}</h2>
        <ul>
          {text.technologies.map((technology) => (
            <li key={technology}>{technology}</li>
          ))}
        </ul>
      </section>

      <section className="about-section">
        <h2>{text.indiaTitle}</h2>
        <p>{text.indiaText}</p>
      </section>
    </div>
  );
}

export default About;
