import "./Navbar.css";

import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <h2 className="logo">⚖️ LawMate AI</h2>

      <div className="nav-links">
        <Link to="/">Home</Link>

        <Link to="/chat">Chat</Link>

        <Link to="/upload">Upload</Link>

        <Link to="/about">About</Link>
      </div>
    </nav>
  );
}

export default Navbar;