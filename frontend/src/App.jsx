import "./App.css";
import Hero from "./components/Hero";
import ActionButton from "./components/ActionButton";

function App() {
  return (
    <div className="app">
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
    </div>
  );
}

export default App;