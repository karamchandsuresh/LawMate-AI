import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "../context/LanguageContext";
import { featureTranslations } from "../context/featureTranslations";
import "./Complaint.css";

function Complaint() {
  const evidenceInputRef = useRef(null);
  const { language } = useLanguage();
  const text = featureTranslations[language]?.complaint || featureTranslations.en.complaint;

  const [formData, setFormData] = useState({
    complaint_type: "consumer",
    problem_description: "",
    complainant_name: "",
    complainant_address: "",
    complainant_contact: "",
    opposite_party: "",
    incident_date: "",
    incident_location: "",
    amount_involved: "",
    evidence: "",
    desired_relief: "",
  });

  const [evidenceFiles, setEvidenceFiles] = useState([]);
  const [draft, setDraft] = useState("");
  const [evidenceNotice, setEvidenceNotice] = useState("");
  const [processedEvidence, setProcessedEvidence] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const allowedExtensions = ["pdf", "docx", "jpg", "jpeg", "png"];
  const maxEvidenceFiles = 5;
  const maxFileSize = 10 * 1024 * 1024;

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previousData) => ({ ...previousData, [name]: value }));
  };

  const validateEvidenceFiles = (files) => {
    if (files.length > maxEvidenceFiles) return text.maxFilesError;

    for (const file of files) {
      const extension = file.name.split(".").pop().toLowerCase();

      if (!allowedExtensions.includes(extension)) {
        return `${text.unsupportedPrefix} ${file.name}. ${text.unsupportedSuffix}`;
      }

      if (file.size > maxFileSize) {
        return `${text.tooLargePrefix} ${file.name}. ${text.tooLargeSuffix}`;
      }
    }

    return "";
  };

  const handleEvidenceSelect = (event) => {
    const files = Array.from(event.target.files || []);
    const validationError = validateEvidenceFiles(files);

    if (validationError) {
      setError(validationError);
      setEvidenceFiles([]);
      return;
    }

    setEvidenceFiles(files);
    setError("");
    setDraft("");
    setProcessedEvidence([]);
    setEvidenceNotice("");
  };

  const handleEvidenceBrowse = () => {
    evidenceInputRef.current?.click();
  };

  const removeEvidenceFile = (indexToRemove) => {
    setEvidenceFiles((previousFiles) =>
      previousFiles.filter((_, index) => index !== indexToRemove)
    );
    setDraft("");
    setProcessedEvidence([]);
    setEvidenceNotice("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setDraft("");
    setProcessedEvidence([]);
    setEvidenceNotice("");

    if (formData.problem_description.trim().length < 20) {
      setError(text.problemError);
      return;
    }

    setIsLoading(true);
    const requestData = new FormData();

    Object.entries(formData).forEach(([key, value]) => {
      requestData.append(key, value);
    });

    requestData.append("language", language);

    evidenceFiles.forEach((file) => {
      requestData.append("evidence_files", file);
    });

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-complaint", {
        method: "POST",
        body: requestData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || text.failed);
      }

      setDraft(data.draft || text.noDraft);
      setProcessedEvidence(data.evidence_files || []);
      setEvidenceNotice(data.evidence_notice || "");
    } catch (err) {
      console.error("Complaint generation error:", err);
      setError(err.message || text.genericError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="complaint-page">
      <h1>{text.title}</h1>
      <p className="complaint-intro">{text.intro}</p>

      <form className="complaint-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <h2>{text.typeSection}</h2>
          <label>
            {text.selectType}
            <select name="complaint_type" value={formData.complaint_type} onChange={handleChange}>
              <option value="consumer">{text.types.consumer}</option>
              <option value="cybercrime">{text.types.cybercrime}</option>
              <option value="police">{text.types.police}</option>
              <option value="workplace">{text.types.workplace}</option>
              <option value="general">{text.types.general}</option>
            </select>
          </label>
        </div>

        <div className="form-section">
          <h2>{text.complainantDetails}</h2>
          <div className="form-grid">
            <label>
              {text.fullName}
              <input type="text" name="complainant_name" value={formData.complainant_name} onChange={handleChange} placeholder={text.namePlaceholder} />
            </label>
            <label>
              {text.contact}
              <input type="text" name="complainant_contact" value={formData.complainant_contact} onChange={handleChange} placeholder={text.contactPlaceholder} />
            </label>
          </div>
          <label>
            {text.address}
            <textarea name="complainant_address" value={formData.complainant_address} onChange={handleChange} placeholder={text.addressPlaceholder} rows="3" />
          </label>
        </div>

        <div className="form-section">
          <h2>{text.complaintDetails}</h2>
          <label>
            {text.oppositeParty}
            <input type="text" name="opposite_party" value={formData.opposite_party} onChange={handleChange} placeholder={text.oppositePartyPlaceholder} />
          </label>

          <div className="form-grid">
            <label>
              {text.incidentDate}
              <input type="date" name="incident_date" value={formData.incident_date} onChange={handleChange} />
            </label>
            <label>
              {text.incidentLocation}
              <input type="text" name="incident_location" value={formData.incident_location} onChange={handleChange} placeholder={text.incidentLocationPlaceholder} />
            </label>
          </div>

          <label>
            {text.amount}
            <input type="text" name="amount_involved" value={formData.amount_involved} onChange={handleChange} placeholder={text.amountPlaceholder} />
          </label>

          <label>
            {text.problem}<span className="required-mark">*</span>
            <textarea name="problem_description" value={formData.problem_description} onChange={handleChange} placeholder={text.problemPlaceholder} rows="7" required />
          </label>
        </div>

        <div className="form-section evidence-section">
          <h2>{text.evidenceSection}</h2>
          <p className="evidence-explanation">{text.evidenceExplanation}</p>

          <label>
            {text.evidenceDescription}
            <textarea name="evidence" value={formData.evidence} onChange={handleChange} placeholder={text.evidencePlaceholder} rows="4" />
          </label>

          <div className="evidence-upload-box">
            <h3>{text.uploadEvidence}</h3>
            <p>{text.uploadEvidenceText}</p>
            <input ref={evidenceInputRef} type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" multiple onChange={handleEvidenceSelect} className="hidden-file-input" />
            <button type="button" className="evidence-browse-button" onClick={handleEvidenceBrowse} disabled={isLoading}>
              {text.chooseFiles}
            </button>
            <p className="evidence-file-note">PDF • DOCX • JPG • JPEG • PNG<br />{text.fileNote}</p>
          </div>

          {evidenceFiles.length > 0 && (
            <div className="selected-evidence-files">
              <h3>{text.selectedFiles}</h3>
              {evidenceFiles.map((file, index) => (
                <div className="evidence-file-item" key={`${file.name}-${index}`}>
                  <div>
                    <strong>{file.name}</strong>
                    <span>{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                  <button type="button" onClick={() => removeEvidenceFile(index)} disabled={isLoading}>{text.remove}</button>
                </div>
              ))}
            </div>
          )}

          <label>
            {text.desiredRelief}
            <textarea name="desired_relief" value={formData.desired_relief} onChange={handleChange} placeholder={text.desiredReliefPlaceholder} rows="4" />
          </label>
        </div>

        {error && <div className="complaint-error">⚠️ {error}</div>}

        <button type="submit" className="generate-complaint-button" disabled={isLoading}>
          {isLoading ? text.generating : text.generate}
        </button>
      </form>

      {isLoading && (
        <div className="complaint-loading">
          <h3>{text.preparing}</h3>
          <p>{text.preparingText}</p>
        </div>
      )}

      {processedEvidence.length > 0 && (
        <div className="evidence-processing-result">
          <h3>{text.evidenceProcessing}</h3>
          {processedEvidence.map((item, index) => (
            <div className="processed-evidence-item" key={`${item.filename}-${index}`}>
              <strong>{item.filename}</strong>
              <span>{item.status}</span>
            </div>
          ))}
          {evidenceNotice && <p className="evidence-authenticity-note">⚠️ {evidenceNotice}</p>}
        </div>
      )}

      {draft && (
        <div className="complaint-result">
          <h2>{text.draftTitle}</h2>
          <div className="complaint-content"><ReactMarkdown>{draft}</ReactMarkdown></div>
        </div>
      )}

      <div className="complaint-note">{text.finalNote}</div>
    </div>
  );
}

export default Complaint;
