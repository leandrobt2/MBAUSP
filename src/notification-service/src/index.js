require('dotenv').config();
const express = require('express');
const { setupQueues } = require('./queues');
const { setupLogger } = require('./utils/logger');
const notificationRoutes = require('./routes/notifications');

const app = express();
const port = process.env.PORT || 3001;
const logger = setupLogger();

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// API routes
app.use('/api/notifications', notificationRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

async function startServer() {
  try {
    // Setup message queues
    await setupQueues();
    
    // Start the server
    app.listen(port, () => {
      logger.info(`Notification service running on port ${port}`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();