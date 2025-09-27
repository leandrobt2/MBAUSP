require('dotenv').config();
const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const config = require('./config');
const routes = require('./routes');
const errorHandler = require('./middleware/error');
const logger = require('./services/logger');
const { initializeDatabase } = require('./services/database');
const { initializeQueue } = require('./services/queue');

const app = express();

// Middleware
app.use(cors(config.cors));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// API Documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(require('./swagger.json')));

// Routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);

async function startServer() {
    try {
        // Initialize database connection
        await initializeDatabase();
        
        // Initialize message queue
        await initializeQueue();
        
        // Start the server
        app.listen(config.server.port, () => {
            logger.info(`API Gateway running on port ${config.server.port}`);
        });
    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Handle unexpected errors
process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (error) => {
    logger.error('Unhandled Rejection:', error);
    process.exit(1);
});

startServer();