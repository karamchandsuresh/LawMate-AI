import "./App.css";

import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Upload from "./pages/Upload";
import About from "./pages/About";

import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navbar />

        <main className="hero-section">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;