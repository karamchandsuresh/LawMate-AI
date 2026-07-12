function Upload() {
  return (
    <div className="upload-page">
      <h1>📄 Upload Legal Document</h1>

      <p>
        Upload your legal documents and receive AI-powered summaries
        and explanations in simple language.
      </p>

      <div className="upload-box">
        <h2>📂 Drag & Drop Your Legal Document</h2>

        <p>or click the button below to browse files</p>

        <button>Browse Files</button>

        <p className="upload-note">
          Supported: PDF, DOCX, JPG, JPEG, PNG
        </p>
      </div>

      <div className="supported-files">
        <h3>Supported File Types</h3>

        <p>
          PDF • DOCX • JPG • JPEG • PNG
        </p>
      </div>

      <div className="security-note">
        🔒 Your uploaded documents are processed securely and used
        only for legal analysis.
      </div>
    </div>
  );
}

export default Upload;