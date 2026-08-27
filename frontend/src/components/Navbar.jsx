import "./Navbar.css";
import { NavLink } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import { languages } from "../context/translations";
import { useAIModel } from "../context/AIModelContext";

function Navbar() {
  const { language, setLanguage, t } = useLanguage();
  const {
    aiMode,
    setAiMode,
    aiModelOptions,
  } = useAIModel();

  return (
    <nav className="navbar">
      <NavLink
        to="/"
        className="brand-link"
        aria-label="LawMate AI Home"
      >
        <span
          className="brand-mark"
          aria-hidden="true"
        >
          ⚖
        </span>

        <span className="brand-copy">
          <strong>
            LawMate <em>AI</em>
          </strong>
          <small>Indian Legal Assistant</small>
        </span>
      </NavLink>

      <div className="nav-links">
        <NavLink to="/" end>
          {t.nav.home}
        </NavLink>

        <NavLink to="/chat">
          {t.nav.chat}
        </NavLink>

        <NavLink to="/upload">
          {t.nav.upload}
        </NavLink>

        <NavLink to="/complaint">
          {t.nav.complaint}
        </NavLink>

        <NavLink to="/case-assessment">
          {t.nav.caseAssessment}
        </NavLink>

        <NavLink to="/about">
          {t.nav.about}
        </NavLink>
      </div>

      <div className="nav-controls">
        <div className="nav-model-wrap">
          <span
            className="model-icon"
            aria-hidden="true"
          >
            🤖
          </span>

          <div className="model-control">
            <span className="model-control-label">
              AI Mode
            </span>

            <select
              className="model-selector"
              value={aiMode}
              onChange={(event) =>
                setAiMode(event.target.value)
              }
              aria-label="Select LawMate AI model mode"
            >
              {aiModelOptions.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.shortLabel}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="nav-language-wrap">
          <span
            className="language-globe"
            aria-hidden="true"
          >
            🌐
          </span>

          <select
            className="language-selector"
            value={language}
            onChange={(event) =>
              setLanguage(event.target.value)
            }
            aria-label={t.common.language}
          >
            {languages.map((item) => (
              <option
                key={item.code}
                value={item.code}
              >
                {item.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
