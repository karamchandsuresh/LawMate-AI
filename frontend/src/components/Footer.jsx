import "./Footer.css";
import { Link } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";

function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-brand-row">
            <span className="footer-mark" aria-hidden="true">⚖</span>
            <h3>LawMate <span>AI</span></h3>
          </div>
          <p>{t.footer}</p>
        </div>

        <div className="footer-links">
          <Link to="/">{t.nav.home}</Link>
          <Link to="/chat">{t.nav.chat}</Link>
          <Link to="/upload">{t.nav.upload}</Link>
          <Link to="/complaint">{t.nav.complaint}</Link>
          <Link to="/case-assessment">{t.nav.caseAssessment}</Link>
          <Link to="/about">{t.nav.about}</Link>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© 2026 LawMate AI</span>
        <span>🇮🇳</span>
      </div>
    </footer>
  );
}

export default Footer;
