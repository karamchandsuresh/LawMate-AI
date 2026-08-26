import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "../context/LanguageContext";
import "./Upload.css";

const uploadVisualText = {
  en: {
    panelTitle: "What LawMate can analyze",
    panelIntro: "Common document types supported by the analyzer",
    legalDocuments: "Legal Documents",
    legalDocumentsHint: "Contracts, agreements, notices",
    identityProofs: "Identity Proofs",
    identityProofsHint: "Aadhaar, PAN, passports",
    courtDocuments: "Court Documents",
    courtDocumentsHint: "Orders, judgments, summons",
    evidenceFiles: "Evidence Files",
    evidenceFilesHint: "Photos, screenshots, records",
    maxSize: "Maximum file size: 10 MB",
  },

  hi: {
    panelTitle: "LawMate क्या विश्लेषित कर सकता है",
    panelIntro: "विश्लेषक द्वारा समर्थित सामान्य दस्तावेज़ प्रकार",
    legalDocuments: "कानूनी दस्तावेज़",
    legalDocumentsHint: "अनुबंध, समझौते, नोटिस",
    identityProofs: "पहचान दस्तावेज़",
    identityProofsHint: "आधार, पैन, पासपोर्ट",
    courtDocuments: "अदालती दस्तावेज़",
    courtDocumentsHint: "आदेश, निर्णय, समन",
    evidenceFiles: "साक्ष्य फ़ाइलें",
    evidenceFilesHint: "फोटो, स्क्रीनशॉट, रिकॉर्ड",
    maxSize: "अधिकतम फ़ाइल आकार: 10 MB",
  },

  ml: {
    panelTitle: "LawMate വിശകലനം ചെയ്യാവുന്നവ",
    panelIntro: "അനലൈസർ പിന്തുണയ്ക്കുന്ന സാധാരണ രേഖാ തരങ്ങൾ",
    legalDocuments: "നിയമ രേഖകൾ",
    legalDocumentsHint: "കരാറുകൾ, ഉടമ്പടികൾ, നോട്ടീസുകൾ",
    identityProofs: "തിരിച്ചറിയൽ രേഖകൾ",
    identityProofsHint: "ആധാർ, PAN, പാസ്‌പോർട്ട്",
    courtDocuments: "കോടതി രേഖകൾ",
    courtDocumentsHint: "ഉത്തരവുകൾ, വിധികൾ, സമൻസ്",
    evidenceFiles: "തെളിവ് ഫയലുകൾ",
    evidenceFilesHint: "ഫോട്ടോകൾ, സ്ക്രീൻഷോട്ടുകൾ, രേഖകൾ",
    maxSize: "പരമാവധി ഫയൽ വലുപ്പം: 10 MB",
  },

  ta: {
    panelTitle: "LawMate பகுப்பாய்வு செய்யக்கூடியவை",
    panelIntro: "பகுப்பாய்வி ஆதரிக்கும் பொதுவான ஆவண வகைகள்",
    legalDocuments: "சட்ட ஆவணங்கள்",
    legalDocumentsHint: "ஒப்பந்தங்கள், உடன்படிக்கைகள், அறிவிப்புகள்",
    identityProofs: "அடையாள ஆவணங்கள்",
    identityProofsHint: "ஆதார், PAN, பாஸ்போர்ட்",
    courtDocuments: "நீதிமன்ற ஆவணங்கள்",
    courtDocumentsHint: "உத்தரவுகள், தீர்ப்புகள், சம்மன்கள்",
    evidenceFiles: "ஆதார கோப்புகள்",
    evidenceFilesHint: "புகைப்படங்கள், ஸ்கிரீன்ஷாட்கள், பதிவுகள்",
    maxSize: "அதிகபட்ச கோப்பு அளவு: 10 MB",
  },

  kn: {
    panelTitle: "LawMate ವಿಶ್ಲೇಷಿಸಬಹುದಾದವು",
    panelIntro: "ವಿಶ್ಲೇಷಕ ಬೆಂಬಲಿಸುವ ಸಾಮಾನ್ಯ ದಾಖಲೆ ಪ್ರಕಾರಗಳು",
    legalDocuments: "ಕಾನೂನು ದಾಖಲೆಗಳು",
    legalDocumentsHint: "ಒಪ್ಪಂದಗಳು, ಕರಾರುಗಳು, ನೋಟಿಸ್‌ಗಳು",
    identityProofs: "ಗುರುತಿನ ದಾಖಲೆಗಳು",
    identityProofsHint: "ಆಧಾರ್, PAN, ಪಾಸ್‌ಪೋರ್ಟ್",
    courtDocuments: "ನ್ಯಾಯಾಲಯದ ದಾಖಲೆಗಳು",
    courtDocumentsHint: "ಆದೇಶಗಳು, ತೀರ್ಪುಗಳು, ಸಮನ್ಸ್",
    evidenceFiles: "ಸಾಕ್ಷ್ಯ ಫೈಲ್‌ಗಳು",
    evidenceFilesHint: "ಫೋಟೋಗಳು, ಸ್ಕ್ರೀನ್‌ಶಾಟ್‌ಗಳು, ದಾಖಲೆಗಳು",
    maxSize: "ಗರಿಷ್ಠ ಫೈಲ್ ಗಾತ್ರ: 10 MB",
  },

  te: {
    panelTitle: "LawMate విశ్లేషించగలవి",
    panelIntro: "విశ్లేషకుడు మద్దతు ఇచ్చే సాధారణ పత్రాల రకాలు",
    legalDocuments: "న్యాయ పత్రాలు",
    legalDocumentsHint: "ఒప్పందాలు, అగ్రిమెంట్లు, నోటీసులు",
    identityProofs: "గుర్తింపు పత్రాలు",
    identityProofsHint: "ఆధార్, PAN, పాస్‌పోర్ట్",
    courtDocuments: "కోర్టు పత్రాలు",
    courtDocumentsHint: "ఆదేశాలు, తీర్పులు, సమన్లు",
    evidenceFiles: "సాక్ష్య ఫైళ్లు",
    evidenceFilesHint: "ఫోటోలు, స్క్రీన్‌షాట్లు, రికార్డులు",
    maxSize: "గరిష్ట ఫైల్ పరిమాణం: 10 MB",
  },
};

function Upload() {
  const fileInputRef = useRef(null);
  const { t, language } = useLanguage();
  const text = t.uploadPage;
  const visualText = uploadVisualText[language] || uploadVisualText.en;

  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const allowedExtensions = ["pdf", "docx", "jpg", "jpeg", "png"];

  const validateFile = (file) => {
    if (!file) return text.selectFile;

    const extension = file.name.split(".").pop().toLowerCase();
    if (!allowedExtensions.includes(extension)) return text.unsupported;

    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) return text.tooLarge;

    return "";
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    const validationError = validateFile(file);

    if (validationError) {
      setSelectedFile(null);
      setAnalysis("");
      setError(validationError);
      return;
    }

    setSelectedFile(file);
    setAnalysis("");
    setError("");
  };

  const handleBrowseClick = () => fileInputRef.current?.click();

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError(text.selectFirst);
      return;
    }

    setIsLoading(true);
    setError("");
    setAnalysis("");

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("language", language);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze-document", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || text.failed);
      }

      setAnalysis(data.analysis || text.noResponse);
    } catch (err) {
      console.error("Document analysis error:", err);
      setError(err.message || text.genericError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files[0];
    const validationError = validateFile(file);

    if (validationError) {
      setSelectedFile(null);
      setAnalysis("");
      setError(validationError);
      return;
    }

    setSelectedFile(file);
    setAnalysis("");
    setError("");
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  return (
    <div className="upload-page">
      <div className="upload-page-heading">
        <div className="upload-heading-icon" aria-hidden="true">
          📄
        </div>

        <div>
          <h1>{text.title.replace(/^📄\s*/, "")}</h1>
          <p>{text.description}</p>
        </div>
      </div>

      <div className="upload-workspace">
        <section
          className="upload-box"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          <div className="upload-drop-icon" aria-hidden="true">
            ☁
          </div>

          <h2>{text.dropTitle.replace(/^📂\s*/, "")}</h2>
          <p className="upload-browse-hint">{text.browseHint}</p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.jpg,.jpeg,.png"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />

          <button
            type="button"
            className="browse-button"
            onClick={handleBrowseClick}
            disabled={isLoading}
          >
            {text.browse}
          </button>

          <p className="upload-note">{text.supported}</p>
          <p className="upload-size-note">{visualText.maxSize}</p>

          {selectedFile && (
            <div className="selected-file">
              <div className="selected-file-icon" aria-hidden="true">
                ✓
              </div>

              <div className="selected-file-details">
                <p>
                  <strong>{text.selectedFile}</strong> {selectedFile.name}
                </p>

                <p>
                  <strong>{text.size}</strong>{" "}
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
          )}

          {selectedFile && (
            <button
              type="button"
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={isLoading}
            >
              {isLoading ? text.analyzing : text.analyze}
            </button>
          )}
        </section>

        <aside className="upload-info-card">
          <div className="upload-info-heading">
            <span className="upload-info-heading-icon" aria-hidden="true">
              ⚖
            </span>

            <div>
              <h2>{visualText.panelTitle}</h2>
              <p>{visualText.panelIntro}</p>
            </div>
          </div>

          <div className="upload-info-list">
            <div className="upload-info-item">
              <div className="upload-info-icon legal" aria-hidden="true">
                📑
              </div>

              <div>
                <h3>{visualText.legalDocuments}</h3>
                <p>{visualText.legalDocumentsHint}</p>
              </div>
            </div>

            <div className="upload-info-item">
              <div className="upload-info-icon identity" aria-hidden="true">
                🪪
              </div>

              <div>
                <h3>{visualText.identityProofs}</h3>
                <p>{visualText.identityProofsHint}</p>
              </div>
            </div>

            <div className="upload-info-item">
              <div className="upload-info-icon court" aria-hidden="true">
                🏛
              </div>

              <div>
                <h3>{visualText.courtDocuments}</h3>
                <p>{visualText.courtDocumentsHint}</p>
              </div>
            </div>

            <div className="upload-info-item">
              <div className="upload-info-icon evidence" aria-hidden="true">
                🖼
              </div>

              <div>
                <h3>{visualText.evidenceFiles}</h3>
                <p>{visualText.evidenceFilesHint}</p>
              </div>
            </div>
          </div>
        </aside>
      </div>

      {error && <div className="upload-error">⚠️ {error}</div>}

      {isLoading && (
        <div className="analysis-loading">
          <div className="analysis-loading-icon" aria-hidden="true">
            ⚖
          </div>

          <div>
            <h3>{text.loadingTitle.replace(/^🔍\s*/, "")}</h3>
            <p>{text.loadingText}</p>
          </div>
        </div>
      )}

      {analysis && (
        <div className="analysis-result">
          <div className="analysis-result-heading">
            <div className="analysis-result-icon" aria-hidden="true">
              📑
            </div>

            <h2>{text.resultTitle.replace(/^📑\s*/, "")}</h2>
          </div>

          <div className="analysis-content">
            <ReactMarkdown>{analysis}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="security-note">
        <span aria-hidden="true">🔒</span>
        <span>{text.security.replace(/^🔒\s*/, "")}</span>
      </div>
    </div>
  );
}

export default Upload;
