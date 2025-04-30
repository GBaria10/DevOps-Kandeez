// App.jsx

import React, { useState } from "react";
import KeyList from './components/KeyList';
import HomePage from "./components/HomePage";
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [showMainPage, setShowMainPage] = useState(false);

  return (
    <div className="App">
      <nav className="navbar navbar-dark custom-navbar">
        <div className="container d-flex justify-content-center">
          <span className="navbar-brand mb-0 h1 custom-title">
            Kandeez Ransomware
          </span>
        </div>
      </nav>

      {showMainPage ? <KeyList /> : <HomePage onContinue={() => setShowMainPage(true)} />}
    </div>
  );
}

export default App;
