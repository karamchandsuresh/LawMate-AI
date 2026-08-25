import "./Navbar.css";
import { NavLink } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { languages } from "../context/translations";

function Navbar() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <nav className="navbar">
      <NavLink to="/" className="brand-link" aria-label="LawMate AI Home">
        <span className="brand-mark" aria-hidden="true">⚖</span>
        <span className="brand-copy">
          <strong>LawMate <em>AI</em></strong>
          <small>Indian Legal Assistant</small>
        </span>
      </NavLink>

      <div className="nav-links">
        <NavLink to="/" end>{t.nav.home}</NavLink>
        <NavLink to="/chat">{t.nav.chat}</NavLink>
        <NavLink to="/upload">{t.nav.upload}</NavLink>
        <NavLink to="/complaint">{t.nav.complaint}</NavLink>
        <NavLink to="/case-assessment">{t.nav.caseAssessment}</NavLink>
        <NavLink to="/about">{t.nav.about}</NavLink>
      </div>

      <div className="nav-language-wrap">
        <span className="language-globe" aria-hidden="true">🌐</span>
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
