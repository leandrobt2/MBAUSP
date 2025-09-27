require('dotenv').config();
const express = require('express');
const { setupLogger } = require('./utils/logger');
const reportRoutes = require('./routes/reports');

const app = express();
const port = process.env.PORT || 3002;
const logger = setupLogger();

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// API routes
app.use('/api/reports', reportRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(port, () => {
  logger.info(`Reporting service running on port ${port}`);
});