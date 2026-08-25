import "./Navbar.css";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { languages } from "../context/translations";

function Navbar() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <nav className="navbar">
      <h2 className="logo">⚖️ LawMate AI</h2>

      <div className="nav-links">
        <Link to="/">{t.nav.home}</Link>
        <Link to="/chat">{t.nav.chat}</Link>
        <Link to="/upload">{t.nav.upload}</Link>
        <Link to="/complaint">{t.nav.complaint}</Link>
        <Link to="/case-assessment">{t.nav.caseAssessment}</Link>
        <Link to="/about">{t.nav.about}</Link>

        <select
          className="language-selector"
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
          aria-label={t.common.language}
        >
          {languages.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </div>
    </nav>
  );
}

export default Navbar;
