import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "../context/LanguageContext";
import { featureTranslations } from "../context/featureTranslations";
import "./Complaint.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function Complaint() {
  const evidenceInputRef = useRef(null);
  const { language } = useLanguage();
  const text =
    featureTranslations[language]?.complaint ||
    featureTranslations.en.complaint;

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
  const [currentStep, setCurrentStep] = useState(1);

  const allowedExtensions = ["pdf", "docx", "jpg", "jpeg", "png"];
  const maxEvidenceFiles = 5;
  const maxFileSize = 10 * 1024 * 1024;

  const complaintTypeIcons = {
    consumer: "🛍️",
    cybercrime: "💻",
    police: "👮",
    workplace: "💼",
    general: "⚖️",
  };

  const complaintTypes = [
    ["consumer", text.types.consumer],
    ["cybercrime", text.types.cybercrime],
    ["police", text.types.police],
    ["workplace", text.types.workplace],
    ["general", text.types.general],
  ];

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previousData) => ({ ...previousData, [name]: value }));
  };

  const chooseComplaintType = (value) => {
    setFormData((previousData) => ({
      ...previousData,
      complaint_type: value,
    }));
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

  const goToDetails = () => {
    setError("");
    setCurrentStep(2);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const goToReview = () => {
    if (formData.problem_description.trim().length < 20) {
      setError(text.problemError);
      return;
    }

    setError("");
    setCurrentStep(3);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const generateComplaint = async () => {
    if (isLoading) return;

    setError("");
    setDraft("");
    setProcessedEvidence([]);
    setEvidenceNotice("");

    if (formData.problem_description.trim().length < 20) {
      setError(text.problemError);
      setCurrentStep(2);
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
      const response = await fetch(
        `${API_BASE_URL}/generate-complaint`,
        {
          method: "POST",
          body: requestData,
        }
      );

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
      <div className="complaint-heading">
        <div className="complaint-heading-icon">📝</div>
        <div>
          <h1>{text.title}</h1>
          <p className="complaint-intro">{text.intro}</p>
        </div>
      </div>

      <div className="complaint-workspace">
        <aside className="complaint-steps" aria-label="Complaint progress">
          <button
            type="button"
            className={`complaint-step ${currentStep === 1 ? "active" : ""} ${
              currentStep > 1 ? "completed" : ""
            }`}
            onClick={() => setCurrentStep(1)}
          >
            <span className="step-number">{currentStep > 1 ? "✓" : "1"}</span>
            <span>
              <strong>{text.typeSection}</strong>
              <small>{text.selectType}</small>
            </span>
          </button>

          <button
            type="button"
            className={`complaint-step ${currentStep === 2 ? "active" : ""} ${
              currentStep > 2 ? "completed" : ""
            }`}
            onClick={() => currentStep >= 2 && setCurrentStep(2)}
            disabled={currentStep < 2}
          >
            <span className="step-number">{currentStep > 2 ? "✓" : "2"}</span>
            <span>
              <strong>{text.complaintDetails}</strong>
              <small>{text.complainantDetails}</small>
            </span>
          </button>

          <button
            type="button"
            className={`complaint-step ${currentStep === 3 ? "active" : ""}`}
            onClick={() => currentStep >= 3 && setCurrentStep(3)}
            disabled={currentStep < 3}
          >
            <span className="step-number">3</span>
            <span>
              <strong>Review</strong>
              <small>{text.generate}</small>
            </span>
          </button>
        </aside>

        <main className="complaint-main">
          <div className="complaint-form">
            {currentStep === 1 && (
              <section className="complaint-panel">
                <div className="panel-heading">
                  <span className="panel-icon">⚖️</span>
                  <div>
                    <h2>{text.typeSection}</h2>
                    <p>{text.selectType}</p>
                  </div>
                </div>

                <div className="complaint-type-grid">
                  {complaintTypes.map(([value, label]) => (
                    <button
                      type="button"
                      key={value}
                      className={`complaint-type-card ${
                        formData.complaint_type === value ? "selected" : ""
                      }`}
                      onClick={() => chooseComplaintType(value)}
                    >
                      <span className="type-icon">
                        {complaintTypeIcons[value]}
                      </span>
                      <strong>{label}</strong>
                      <span className="type-check">
                        {formData.complaint_type === value ? "✓" : "→"}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="complaint-actions">
                  <button
                    type="button"
                    className="complaint-primary-button"
                    onClick={goToDetails}
                  >
                    Next →
                  </button>
                </div>
              </section>
            )}

            {currentStep === 2 && (
              <>
                <section className="complaint-panel">
                  <div className="panel-heading">
                    <span className="panel-icon">👤</span>
                    <div>
                      <h2>{text.complainantDetails}</h2>
                    </div>
                  </div>

                  <div className="form-grid">
                    <label>
                      {text.fullName}
                      <input
                        type="text"
                        name="complainant_name"
                        value={formData.complainant_name}
                        onChange={handleChange}
                        placeholder={text.namePlaceholder}
                      />
                    </label>

                    <label>
                      {text.contact}
                      <input
                        type="text"
                        name="complainant_contact"
                        value={formData.complainant_contact}
                        onChange={handleChange}
                        placeholder={text.contactPlaceholder}
                      />
                    </label>
                  </div>

                  <label>
                    {text.address}
                    <textarea
                      name="complainant_address"
                      value={formData.complainant_address}
                      onChange={handleChange}
                      placeholder={text.addressPlaceholder}
                      rows="3"
                    />
                  </label>
                </section>

                <section className="complaint-panel">
                  <div className="panel-heading">
                    <span className="panel-icon">📋</span>
                    <div>
                      <h2>{text.complaintDetails}</h2>
                    </div>
                  </div>

                  <label>
                    {text.oppositeParty}
                    <input
                      type="text"
                      name="opposite_party"
                      value={formData.opposite_party}
                      onChange={handleChange}
                      placeholder={text.oppositePartyPlaceholder}
                    />
                  </label>

                  <div className="form-grid">
                    <label>
                      {text.incidentDate}
                      <input
                        type="date"
                        name="incident_date"
                        value={formData.incident_date}
                        onChange={handleChange}
                      />
                    </label>

                    <label>
                      {text.incidentLocation}
                      <input
                        type="text"
                        name="incident_location"
                        value={formData.incident_location}
                        onChange={handleChange}
                        placeholder={text.incidentLocationPlaceholder}
                      />
                    </label>
                  </div>

                  <label>
                    {text.amount}
                    <input
                      type="text"
                      name="amount_involved"
                      value={formData.amount_involved}
                      onChange={handleChange}
                      placeholder={text.amountPlaceholder}
                    />
                  </label>

                  <label>
                    {text.problem}
                    <span className="required-mark">*</span>
                    <textarea
                      name="problem_description"
                      value={formData.problem_description}
                      onChange={handleChange}
                      placeholder={text.problemPlaceholder}
                      rows="6"
                    />
                  </label>
                </section>

                <section className="complaint-panel">
                  <div className="panel-heading">
                    <span className="panel-icon">📎</span>
                    <div>
                      <h2>{text.evidenceSection}</h2>
                    </div>
                  </div>

                  <p className="evidence-explanation">
                    {text.evidenceExplanation}
                  </p>

                  <label>
                    {text.evidenceDescription}
                    <textarea
                      name="evidence"
                      value={formData.evidence}
                      onChange={handleChange}
                      placeholder={text.evidencePlaceholder}
                      rows="3"
                    />
                  </label>

                  <div className="evidence-upload-box">
                    <div className="upload-icon">☁</div>
                    <h3>{text.uploadEvidence}</h3>
                    <p>{text.uploadEvidenceText}</p>

                    <input
                      ref={evidenceInputRef}
                      type="file"
                      accept=".pdf,.docx,.jpg,.jpeg,.png"
                      multiple
                      onChange={handleEvidenceSelect}
                      className="hidden-file-input"
                    />

                    <button
                      type="button"
                      className="evidence-browse-button"
                      onClick={handleEvidenceBrowse}
                      disabled={isLoading}
                    >
                      {text.chooseFiles}
                    </button>

                    <p className="evidence-file-note">
                      PDF • DOCX • JPG • JPEG • PNG
                      <br />
                      {text.fileNote}
                    </p>
                  </div>

                  {evidenceFiles.length > 0 && (
                    <div className="selected-evidence-files">
                      <h3>{text.selectedFiles}</h3>

                      {evidenceFiles.map((file, index) => (
                        <div
                          className="evidence-file-item"
                          key={`${file.name}-${index}`}
                        >
                          <div>
                            <strong>{file.name}</strong>
                            <span>{(file.size / 1024).toFixed(1)} KB</span>
                          </div>

                          <button
                            type="button"
                            onClick={() => removeEvidenceFile(index)}
                            disabled={isLoading}
                          >
                            {text.remove}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <label>
                    {text.desiredRelief}
                    <textarea
                      name="desired_relief"
                      value={formData.desired_relief}
                      onChange={handleChange}
                      placeholder={text.desiredReliefPlaceholder}
                      rows="3"
                    />
                  </label>
                </section>

                {error && <div className="complaint-error">⚠️ {error}</div>}

                <div className="complaint-actions split">
                  <button
                    type="button"
                    className="complaint-secondary-button"
                    onClick={() => setCurrentStep(1)}
                  >
                    ← Back
                  </button>

                  <button
                    type="button"
                    className="complaint-primary-button"
                    onClick={goToReview}
                  >
                    Review →
                  </button>
                </div>
              </>
            )}

            {currentStep === 3 && (
              <section className="complaint-panel review-panel">
                <div className="panel-heading">
                  <span className="panel-icon">✓</span>
                  <div>
                    <h2>Review Complaint</h2>
                    <p>Check the information before generating your draft.</p>
                  </div>
                </div>

                <div className="review-grid">
                  <div className="review-item">
                    <span>{text.selectType}</span>
                    <strong>
                      {complaintTypes.find(
                        ([value]) => value === formData.complaint_type
                      )?.[1]}
                    </strong>
                  </div>

                  <div className="review-item">
                    <span>{text.fullName}</span>
                    <strong>{formData.complainant_name || "—"}</strong>
                  </div>

                  <div className="review-item">
                    <span>{text.contact}</span>
                    <strong>{formData.complainant_contact || "—"}</strong>
                  </div>

                  <div className="review-item">
                    <span>{text.oppositeParty}</span>
                    <strong>{formData.opposite_party || "—"}</strong>
                  </div>

                  <div className="review-item">
                    <span>{text.incidentDate}</span>
                    <strong>{formData.incident_date || "—"}</strong>
                  </div>

                  <div className="review-item">
                    <span>{text.incidentLocation}</span>
                    <strong>{formData.incident_location || "—"}</strong>
                  </div>

                  <div className="review-item review-wide">
                    <span>{text.problem}</span>
                    <strong>{formData.problem_description || "—"}</strong>
                  </div>

                  <div className="review-item review-wide">
                    <span>{text.desiredRelief}</span>
                    <strong>{formData.desired_relief || "—"}</strong>
                  </div>

                  <div className="review-item review-wide">
                    <span>{text.selectedFiles}</span>
                    <strong>
                      {evidenceFiles.length > 0
                        ? evidenceFiles.map((file) => file.name).join(", ")
                        : "—"}
                    </strong>
                  </div>
                </div>

                {error && <div className="complaint-error">⚠️ {error}</div>}

                <div className="complaint-actions split">
                  <button
                    type="button"
                    className="complaint-secondary-button"
                    onClick={() => setCurrentStep(2)}
                    disabled={isLoading}
                  >
                    ← Edit Details
                  </button>

                  <button
                    type="button"
                    className="generate-complaint-button"
                    onClick={generateComplaint}
                    disabled={isLoading}
                  >
                    {isLoading ? text.generating : text.generate}
                  </button>
                </div>
              </section>
            )}
          </div>

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
                <div
                  className="processed-evidence-item"
                  key={`${item.filename}-${index}`}
                >
                  <strong>{item.filename}</strong>
                  <span>{item.status}</span>
                </div>
              ))}

              {evidenceNotice && (
                <p className="evidence-authenticity-note">
                  ⚠️ {evidenceNotice}
                </p>
              )}
            </div>
          )}

          {draft && (
            <div className="complaint-result">
              <h2>{text.draftTitle}</h2>
              <div className="complaint-content">
                <ReactMarkdown>{draft}</ReactMarkdown>
              </div>
            </div>
          )}
        </main>
      </div>

      <div className="complaint-note">{text.finalNote}</div>
    </div>
  );
}

export default Complaint;
