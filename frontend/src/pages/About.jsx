import "./About.css";


function About() {
  return (
    <div className="about-page">
      <h1>⚖️ About LawMate AI</h1>

      <p className="about-intro">
        LawMate AI is a multilingual AI-powered legal assistant designed
        to make Indian legal information simple, accessible, and affordable
        for everyone.
      </p>

      <section className="about-section">
        <h2>🎯 Our Mission</h2>

        <p>
          Our goal is to bridge the gap between citizens and the legal
          system by providing reliable legal guidance using Artificial
          Intelligence and Retrieval-Augmented Generation (RAG).
        </p>
      </section>

      <section className="about-section">
        <h2>✨ Key Features</h2>

        <ul>
          <li>AI-powered Legal Question Answering</li>
          <li>Legal Document Analysis</li>
          <li>Complaint & RTI Generator</li>
          <li>Case Outcome Prediction</li>
          <li>Multilingual Support</li>
        </ul>
      </section>

      <section className="about-section">
        <h2>🛠 Technologies Used</h2>

        <ul>
          <li>React.js</li>
          <li>FastAPI</li>
          <li>Python</li>
          <li>Gemini / Ollama</li>
          <li>ChromaDB</li>
          <li>RAG</li>
          <li>IndicTrans2</li>
        </ul>
      </section>

      <section className="about-section">
        <h2>🇮🇳 Designed for India</h2>

        <p>
          LawMate AI is built to support Indian laws, legal procedures,
          and multilingual communication, making legal assistance
          accessible to people across the country.
        </p>
      </section>
    </div>
  );
}

export default About;