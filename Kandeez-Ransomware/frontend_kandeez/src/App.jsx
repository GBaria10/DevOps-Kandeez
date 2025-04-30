// App.jsx

import KeyList from './components/KeyList';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'; // make sure you have this

function App() {
  return (
    <div className="App">
      <nav className="navbar navbar-dark custom-navbar">
        <div className="container d-flex justify-content-center">
          <span className="navbar-brand mb-0 h1 custom-title">
            Kandeez Ransomwareeee
          </span>
        </div>
      </nav>
      <KeyList />
    </div>
  );
}

export default App;
