import "./App.css";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Upload from "./pages/Upload";
import About from "./pages/About";

import {
  BrowserRouter,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";


function AppContent() {

  const location = useLocation();

  const isChatPage = location.pathname === "/chat";


  return (

    <div className={`app ${isChatPage ? "chat-app" : ""}`}>

      <Navbar />


      <main
        className={
          isChatPage
            ? "chat-main"
            : "hero-section"
        }
      >

        <Routes>

          <Route
            path="/"
            element={<Home />}
          />

          <Route
            path="/chat"
            element={<Chat />}
          />

          <Route
            path="/upload"
            element={<Upload />}
          />

          <Route
            path="/about"
            element={<About />}
          />

        </Routes>

      </main>


      {!isChatPage && <Footer />}

    </div>

  );

}


function App() {

  return (

    <BrowserRouter>

      <AppContent />

    </BrowserRouter>

  );

}


export default App;