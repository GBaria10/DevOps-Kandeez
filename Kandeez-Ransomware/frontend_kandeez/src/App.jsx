// App.jsx

import React, { useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import KeyList from "./components/KeyList"; // Make sure the path is correct

function App() {
  const [showMainPage, setShowMainPage] = useState(true); // default to true

  return (
    <div className="App">
      <nav className="navbar navbar-dark custom-navbar">
        <div className="container d-flex justify-content-center">
          <span className="navbar-brand mb-0 h1 custom-title">
            Kandeez Ransomware
          </span>
        </div>
      </nav>

      {/* Render KeyList */}
      {showMainPage && <KeyList />}
    </div>
  );
}

export default App;
