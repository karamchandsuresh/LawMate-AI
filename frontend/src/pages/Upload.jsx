import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { useLanguage } from "../context/LanguageContext";
import "./Upload.css";

function Upload() {
  const fileInputRef = useRef(null);
  const { t, language } = useLanguage();
  const text = t.uploadPage;

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
      if (!response.ok) throw new Error(data.detail || text.failed);
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

  const handleDragOver = (event) => event.preventDefault();

  return (
    <div className="upload-page">
      <h1>{text.title}</h1>
      <p>{text.description}</p>

      <div className="upload-box" onDrop={handleDrop} onDragOver={handleDragOver}>
        <h2>{text.dropTitle}</h2>
        <p>{text.browseHint}</p>

        <input ref={fileInputRef} type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" onChange={handleFileSelect} style={{ display: "none" }} />

        <button type="button" onClick={handleBrowseClick} disabled={isLoading}>{text.browse}</button>
        <p className="upload-note">{text.supported}</p>

        {selectedFile && (
          <div className="selected-file">
            <p><strong>{text.selectedFile}</strong> {selectedFile.name}</p>
            <p><strong>{text.size}</strong> {(selectedFile.size / 1024).toFixed(1)} KB</p>
          </div>
        )}

        {selectedFile && (
          <button type="button" className="analyze-button" onClick={handleAnalyze} disabled={isLoading}>
            {isLoading ? text.analyzing : text.analyze}
          </button>
        )}
      </div>

      {error && <div className="upload-error">⚠️ {error}</div>}

      {isLoading && (
        <div className="analysis-loading">
          <h3>{text.loadingTitle}</h3>
          <p>{text.loadingText}</p>
        </div>
      )}

      {analysis && (
        <div className="analysis-result">
          <h2>{text.resultTitle}</h2>
          <div className="analysis-content"><ReactMarkdown>{analysis}</ReactMarkdown></div>
        </div>
      )}

      <div className="supported-files">
        <h3>{text.supportedTypes}</h3>
        <p>PDF • DOCX • JPG • JPEG • PNG</p>
      </div>

      <div className="security-note">{text.security}</div>
    </div>
  );
}

export default Upload;
