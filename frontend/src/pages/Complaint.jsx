import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./Complaint.css";


function Complaint() {
  const evidenceInputRef = useRef(null);

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

  const allowedExtensions = [
    "pdf",
    "docx",
    "jpg",
    "jpeg",
    "png",
  ];

  const maxEvidenceFiles = 5;
  const maxFileSize = 10 * 1024 * 1024;


  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };


  const validateEvidenceFiles = (files) => {
    if (files.length > maxEvidenceFiles) {
      return (
        `You can upload a maximum of ` +
        `${maxEvidenceFiles} evidence files.`
      );
    }

    for (const file of files) {
      const extension = file.name
        .split(".")
        .pop()
        .toLowerCase();

      if (!allowedExtensions.includes(extension)) {
        return (
          `Unsupported evidence file: ${file.name}. ` +
          "Use PDF, DOCX, JPG, JPEG, or PNG."
        );
      }

      if (file.size > maxFileSize) {
        return (
          `Evidence file is too large: ${file.name}. ` +
          "Maximum size is 10 MB per file."
        );
      }
    }

    return "";
  };


  const handleEvidenceSelect = (event) => {
    const files = Array.from(
      event.target.files || []
    );

    const validationError =
      validateEvidenceFiles(files);

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
      previousFiles.filter(
        (_, index) =>
          index !== indexToRemove
      )
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

    if (
      formData.problem_description
        .trim()
        .length < 20
    ) {
      setError(
        "Please provide a more detailed description of the problem."
      );
      return;
    }

    setIsLoading(true);

    const requestData = new FormData();

    Object.entries(formData).forEach(
      ([key, value]) => {
        requestData.append(
          key,
          value
        );
      }
    );

    evidenceFiles.forEach((file) => {
      requestData.append(
        "evidence_files",
        file
      );
    });

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/generate-complaint",
        {
          method: "POST",
          body: requestData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Complaint generation failed."
        );
      }

      setDraft(
        data.draft ||
        "Complaint generated, but no draft was returned."
      );

      setProcessedEvidence(
        data.evidence_files || []
      );

      setEvidenceNotice(
        data.evidence_notice || ""
      );

    } catch (err) {
      console.error(
        "Complaint generation error:",
        err
      );

      setError(
        err.message ||
        "Something went wrong while generating the complaint."
      );

    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="complaint-page">

      <h1>
        📝 AI Complaint Generator
      </h1>

      <p className="complaint-intro">
        Provide the details of your issue and LawMate AI
        will create a structured complaint draft based only
        on the information and supporting material you provide.
      </p>


      <form
        className="complaint-form"
        onSubmit={handleSubmit}
      >

        <div className="form-section">

          <h2>Complaint Type</h2>

          <label>
            Select Complaint Type

            <select
              name="complaint_type"
              value={formData.complaint_type}
              onChange={handleChange}
            >
              <option value="consumer">
                Consumer Complaint
              </option>

              <option value="cybercrime">
                Cybercrime Complaint
              </option>

              <option value="police">
                Police Complaint
              </option>

              <option value="workplace">
                Workplace Complaint
              </option>

              <option value="general">
                General Legal Complaint
              </option>
            </select>
          </label>

        </div>


        <div className="form-section">

          <h2>Complainant Details</h2>

          <div className="form-grid">

            <label>
              Full Name

              <input
                type="text"
                name="complainant_name"
                value={formData.complainant_name}
                onChange={handleChange}
                placeholder="Enter your name"
              />
            </label>


            <label>
              Contact

              <input
                type="text"
                name="complainant_contact"
                value={formData.complainant_contact}
                onChange={handleChange}
                placeholder="Phone or email"
              />
            </label>

          </div>


          <label>
            Address

            <textarea
              name="complainant_address"
              value={formData.complainant_address}
              onChange={handleChange}
              placeholder="Enter your address"
              rows="3"
            />
          </label>

        </div>


        <div className="form-section">

          <h2>Complaint Details</h2>

          <label>
            Opposite Party / Respondent

            <input
              type="text"
              name="opposite_party"
              value={formData.opposite_party}
              onChange={handleChange}
              placeholder="Company, person, employer, seller, etc."
            />
          </label>


          <div className="form-grid">

            <label>
              Incident Date

              <input
                type="date"
                name="incident_date"
                value={formData.incident_date}
                onChange={handleChange}
              />
            </label>


            <label>
              Incident Location

              <input
                type="text"
                name="incident_location"
                value={formData.incident_location}
                onChange={handleChange}
                placeholder="City / location"
              />
            </label>

          </div>


          <label>
            Amount Involved

            <input
              type="text"
              name="amount_involved"
              value={formData.amount_involved}
              onChange={handleChange}
              placeholder="Example: Rs 15000"
            />
          </label>


          <label>
            Problem Description
            <span className="required-mark">*</span>

            <textarea
              name="problem_description"
              value={formData.problem_description}
              onChange={handleChange}
              placeholder="Explain what happened in detail..."
              rows="7"
              required
            />
          </label>

        </div>


        <div className="form-section evidence-section">

          <h2>Supporting Evidence</h2>

          <p className="evidence-explanation">
            Evidence descriptions and uploaded files are
            treated as user-supplied material. LawMate can
            analyze them for drafting, but does not verify
            whether they are genuine, original, unedited,
            or legally admissible.
          </p>


          <label>
            Evidence Description

            <textarea
              name="evidence"
              value={formData.evidence}
              onChange={handleChange}
              placeholder="Example: I have a payment receipt and WhatsApp messages. Pasted text here is treated as unverified user-provided information."
              rows="4"
            />
          </label>


          <div className="evidence-upload-box">

            <h3>
              📎 Upload Supporting Evidence
            </h3>

            <p>
              Upload screenshots, receipts, documents,
              or other supporting files.
            </p>

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
              Choose Evidence Files
            </button>

            <p className="evidence-file-note">
              PDF • DOCX • JPG • JPEG • PNG
              <br />
              Maximum 5 files, 10 MB each
            </p>

          </div>


          {evidenceFiles.length > 0 && (
            <div className="selected-evidence-files">

              <h3>Selected Evidence Files</h3>

              {evidenceFiles.map(
                (file, index) => (
                  <div
                    className="evidence-file-item"
                    key={`${file.name}-${index}`}
                  >
                    <div>
                      <strong>{file.name}</strong>
                      <span>
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        removeEvidenceFile(index)
                      }
                      disabled={isLoading}
                    >
                      Remove
                    </button>
                  </div>
                )
              )}

            </div>
          )}


          <label>
            Desired Relief / Action

            <textarea
              name="desired_relief"
              value={formData.desired_relief}
              onChange={handleChange}
              placeholder="Example: refund, investigation, corrective action..."
              rows="4"
            />
          </label>

        </div>


        {error && (
          <div className="complaint-error">
            ⚠️ {error}
          </div>
        )}


        <button
          type="submit"
          className="generate-complaint-button"
          disabled={isLoading}
        >
          {
            isLoading
              ? "Generating Complaint..."
              : "Generate Complaint"
          }
        </button>

      </form>


      {isLoading && (
        <div className="complaint-loading">

          <h3>
            ⚖️ Preparing your complaint...
          </h3>

          <p>
            LawMate AI is organizing your facts,
            extracting readable evidence content,
            and drafting the complaint.
          </p>

        </div>
      )}


      {processedEvidence.length > 0 && (
        <div className="evidence-processing-result">

          <h3>📎 Evidence Processing</h3>

          {processedEvidence.map(
            (item, index) => (
              <div
                className="processed-evidence-item"
                key={`${item.filename}-${index}`}
              >
                <strong>{item.filename}</strong>
                <span>{item.status}</span>
              </div>
            )
          )}

          {evidenceNotice && (
            <p className="evidence-authenticity-note">
              ⚠️ {evidenceNotice}
            </p>
          )}

        </div>
      )}


      {draft && (
        <div className="complaint-result">

          <h2>
            📄 Generated Complaint Draft
          </h2>

          <div className="complaint-content">
            <ReactMarkdown>
              {draft}
            </ReactMarkdown>
          </div>

        </div>
      )}


      <div className="complaint-note">
        ⚠️ This is a draft generated from information and
        supporting material supplied by the user. LawMate AI
        does not verify evidence authenticity. Review all
        details before submitting the complaint to any authority.
      </div>

    </div>
  );
}


export default Complaint;
