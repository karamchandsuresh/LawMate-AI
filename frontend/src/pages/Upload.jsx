import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./Upload.css";


function Upload() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");


  const allowedExtensions = [
    "pdf",
    "docx",
    "jpg",
    "jpeg",
    "png",
  ];


  const validateFile = (file) => {
    if (!file) {
      return "Please select a file.";
    }

    const extension = file.name
      .split(".")
      .pop()
      .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      return (
        "Unsupported file type. " +
        "Please upload PDF, DOCX, JPG, JPEG, or PNG."
      );
    }

    const maxSize = 10 * 1024 * 1024;

    if (file.size > maxSize) {
      return "File size must be 10 MB or less.";
    }

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


  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };


  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError(
        "Please select a document first."
      );
      return;
    }

    setIsLoading(true);
    setError("");
    setAnalysis("");

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile
    );

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze-document",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Document analysis failed."
        );
      }

      setAnalysis(
        data.analysis ||
        "Analysis completed, but no response was returned."
      );
    } catch (err) {
      console.error(
        "Document analysis error:",
        err
      );

      setError(
        err.message ||
        "Something went wrong while analyzing the document."
      );
    } finally {
      setIsLoading(false);
    }
  };


  const handleDrop = (event) => {
    event.preventDefault();

    const file =
      event.dataTransfer.files[0];

    const validationError =
      validateFile(file);

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

      <h1>
        📄 Upload Legal Document
      </h1>

      <p>
        Upload a document and receive an AI-powered
        summary, key information, potential issues,
        and suggested next steps.
      </p>


      <div
        className="upload-box"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >

        <h2>
          📂 Drag & Drop Your Document
        </h2>

        <p>
          or click the button below to browse files
        </p>


        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
          style={{
            display: "none",
          }}
        />


        <button
          type="button"
          onClick={handleBrowseClick}
          disabled={isLoading}
        >
          Browse Files
        </button>


        <p className="upload-note">
          Supported: PDF, DOCX, JPG, JPEG, PNG
        </p>


        {selectedFile && (
          <div className="selected-file">

            <p>
              <strong>
                Selected File:
              </strong>{" "}
              {selectedFile.name}
            </p>

            <p>
              <strong>
                Size:
              </strong>{" "}
              {(
                selectedFile.size / 1024
              ).toFixed(1)}{" "}
              KB
            </p>

          </div>
        )}


        {selectedFile && (
          <button
            type="button"
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={isLoading}
          >
            {
              isLoading
                ? "Analyzing..."
                : "Analyze Document"
            }
          </button>
        )}

      </div>


      {error && (
        <div className="upload-error">
          ⚠️ {error}
        </div>
      )}


      {isLoading && (
        <div className="analysis-loading">

          <h3>
            🔍 Analyzing document...
          </h3>

          <p>
            Extracting text and reviewing
            the document. This may take a
            few seconds.
          </p>

        </div>
      )}


      {analysis && (
        <div className="analysis-result">

          <h2>
            📑 Document Analysis
          </h2>

          <div className="analysis-content">
            <ReactMarkdown>
              {analysis}
            </ReactMarkdown>
          </div>

        </div>
      )}


      <div className="supported-files">

        <h3>
          Supported File Types
        </h3>

        <p>
          PDF • DOCX • JPG • JPEG • PNG
        </p>

      </div>


      <div className="security-note">

        🔒 Your uploaded document is
        processed only for analysis and is
        not added to the LawMate legal
        knowledge base.

      </div>

    </div>
  );
}


export default Upload;