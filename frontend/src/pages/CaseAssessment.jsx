import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "../context/LanguageContext";
import { featureTranslations } from "../context/featureTranslations";
import "./CaseAssessment.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function CaseAssessment() {
  const { language } = useLanguage();
  const text = featureTranslations[language]?.caseAssessment || featureTranslations.en.caseAssessment;

  const [formData, setFormData] = useState({
    case_type: "consumer",
    case_facts: "",
    user_role: "",
    opposite_party: "",
    evidence_summary: "",
    desired_outcome: "",
  });

  const [assessment, setAssessment] = useState("");
  const [predictionNotice, setPredictionNotice] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previousData) => ({ ...previousData, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setAssessment("");
    setPredictionNotice("");

    if (formData.case_facts.trim().length < 30) {
      setError(text.factsError);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/assess-case`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...formData, language }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || text.failed);

      setAssessment(data.assessment || text.noResult);
      setPredictionNotice(data.prediction_notice || "");
    } catch (err) {
      console.error("Case assessment error:", err);
      setError(err.message || text.genericError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="case-page">
      <h1>{text.title}</h1>
      <p className="case-intro">{text.intro}</p>
      <div className="case-warning">{text.warning}</div>

      <form className="case-form" onSubmit={handleSubmit}>
        <div className="case-form-section">
          <h2>{text.sectionTitle}</h2>

          <label>
            {text.caseType}
            <select name="case_type" value={formData.case_type} onChange={handleChange}>
              <option value="consumer">{text.types.consumer}</option>
              <option value="employment">{text.types.employment}</option>
              <option value="property">{text.types.property}</option>
              <option value="family">{text.types.family}</option>
              <option value="cybercrime">{text.types.cybercrime}</option>
              <option value="criminal">{text.types.criminal}</option>
              <option value="civil">{text.types.civil}</option>
              <option value="general">{text.types.general}</option>
            </select>
          </label>

          <div className="case-form-grid">
            <label>
              {text.yourRole}
              <input type="text" name="user_role" value={formData.user_role} onChange={handleChange} placeholder={text.rolePlaceholder} />
            </label>

            <label>
              {text.oppositeParty}
              <input type="text" name="opposite_party" value={formData.opposite_party} onChange={handleChange} placeholder={text.oppositePartyPlaceholder} />
            </label>
          </div>

          <label>
            {text.caseFacts}<span className="case-required">*</span>
            <textarea name="case_facts" value={formData.case_facts} onChange={handleChange} placeholder={text.factsPlaceholder} rows="8" required />
          </label>

          <label>
            {text.evidenceSummary}
            <textarea name="evidence_summary" value={formData.evidence_summary} onChange={handleChange} placeholder={text.evidencePlaceholder} rows="4" />
          </label>

          <label>
            {text.desiredOutcome}
            <textarea name="desired_outcome" value={formData.desired_outcome} onChange={handleChange} placeholder={text.outcomePlaceholder} rows="3" />
          </label>
        </div>

        {error && <div className="case-error">⚠️ {error}</div>}

        <button type="submit" className="case-submit-button" disabled={isLoading}>
          {isLoading ? text.assessing : text.assess}
        </button>
      </form>

      {isLoading && (
        <div className="case-loading">
          <h3>{text.loadingTitle}</h3>
          <p>{text.loadingText}</p>
        </div>
      )}

      {assessment && (
        <div className="case-result">
          <h2>{text.resultTitle}</h2>
          {predictionNotice && <div className="case-prediction-notice">⚠️ {predictionNotice}</div>}
          <div className="case-result-content"><ReactMarkdown>{assessment}</ReactMarkdown></div>
        </div>
      )}

      <div className="case-footer-note">{text.footer}</div>
    </div>
  );
}

export default CaseAssessment;
