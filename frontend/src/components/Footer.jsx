import "./Footer.css";
import { useLanguage } from "../context/LanguageContext";

function Footer() {
  const { t } = useLanguage();
  return (
    <footer className="footer">
      <h3>⚖️ LawMate AI</h3>
      <p>{t.footer}</p>
      <p className="footer-copy">© 2026 LawMate AI</p>
    </footer>
  );
}
export default Footer;
