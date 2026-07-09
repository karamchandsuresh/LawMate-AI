import Hero from "../components/Hero";
import ActionButton from "../components/ActionButton";

function Home() {
  return (
    <>
      <Hero />

      <div className="buttons">
        <ActionButton
          text="Ask a Legal Question"
          color="#2563EB"
        />

        <ActionButton
          text="Upload Document"
          color="#16A34A"
        />

        <ActionButton
          text="Generate Complaint"
          color="#DC2626"
        />
      </div>
    </>
  );
}

export default Home;