import Hero from "../components/Hero";
import ActionButton from "../components/ActionButton";
import FeatureCard from "../components/FeatureCard";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();
  return (
    <>
      <Hero />

      <div className="buttons">
        <ActionButton
          text="Ask a Legal Question"
          color="#2563EB"
          onClick={() => navigate("/chat")}
        />

        <ActionButton
          text="Upload Document"
          color="#16A34A"
          onClick={() => navigate("/upload")}
        />

        <ActionButton
          text="Generate Complaint"
          color="#DC2626"
        />
      </div>

      <section className="features">
        <FeatureCard
          title="AI Legal Chat"
          description="Ask legal questions and receive AI-powered answers grounded in Indian laws."
        />

        <FeatureCard
          title="Document Analyzer"
          description="Upload PDF, DOCX, or image files and understand legal documents in simple language."
        />

        <FeatureCard
          title="Complaint Generator"
          description="Generate police complaints, RTIs, consumer complaints, and more using AI."
        />
      </section>
    </>
  );
}

export default Home;