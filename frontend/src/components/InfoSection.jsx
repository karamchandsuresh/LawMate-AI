import "./InfoSection.css";
import { useLanguage } from "../context/LanguageContext";
import { languages } from "../context/translations";

function InfoSection() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <section className="info-section">
      <h2>{t.multilingualTitle}</h2>
      <p>{t.multilingualText}</p>

      <div className="languages">
        {languages.map((item) => (
          <button
            type="button"
            key={item.code}
            className={language === item.code ? "language-active" : ""}
            onClick={() => setLanguage(item.code)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </section>
  );
}
export default InfoSection;
