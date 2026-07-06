import "./App.css";
import Hero from "./components/Hero";
import ActionButton from "./components/ActionButton";

function App() {
  return (
    <div className="app">
      <Hero />
    <div className="buttons">
      <ActionButton text="Ask a Legal Question" />
      <ActionButton text="Upload Document" />
      <ActionButton text="Generate Complaint" />
    </div>
    </div>
  );
}

export default App;