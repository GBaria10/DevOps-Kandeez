// src/services/KeyService.js

import axios from 'axios';

const backendPort = import.meta.env.VITE_BACKEND_PORT;
const backendIP = import.meta.env.VITE_BACKEND_IP
const API_URL = `http://${backendIP}:${backendPort}/api`;

export const fetchAllKeys = async () => {
  try {
    const response = await axios.get(`${API_URL}/keys`);
    return response.data;
  } catch (error) {
    console.error('Error fetching keys:', error);
    throw error;
  }
};

export const updateKeyState = async (keyId, state) => {
  try {
    const response = await axios.patch(`${API_URL}/keys/${keyId}/state`, { state });
    return response.data;
  } catch (error) {
    console.error('Error updating key state:', error);
    throw error;
  }
};

export const downloadKey = (key, hostname) => {
  const element = document.createElement('a');
  const file = new Blob([key], { type: 'text/plain' });
  element.href = URL.createObjectURL(file);
  element.download = `key_${hostname}.txt`;
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
};
