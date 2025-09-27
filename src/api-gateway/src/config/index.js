const config = {
    // Server configuration
    server: {
        port: process.env.PORT || 3000,
        env: process.env.NODE_ENV || 'development'
    },

    // Database configuration
    database: {
        url: process.env.DATABASE_URL,
        options: {
            encrypt: false,
            trustServerCertificate: true
        }
    },

    // JWT configuration
    jwt: {
        secret: process.env.JWT_SECRET,
        expiresIn: '24h'
    },

    // Services URLs
    services: {
        mlEngine: process.env.ML_ENGINE_URL || 'http://ml-engine:5000',
        notification: process.env.NOTIFICATION_SERVICE_URL || 'http://notification-service:3001',
        reporting: process.env.REPORTING_SERVICE_URL || 'http://reporting-service:3002'
    },

    // RabbitMQ configuration
    rabbitmq: {
        url: process.env.RABBITMQ_URL || 'amqp://rabbitmq:5672',
        queues: {
            notifications: 'notification_queue',
            modelRetraining: 'model_retraining_queue'
        }
    },

    // CORS configuration
    cors: {
        origin: process.env.CORS_ORIGIN || '*',
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        allowedHeaders: ['Content-Type', 'Authorization']
    },

    // Rate limiting
    rateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100 // limit each IP to 100 requests per windowMs
    }
};

module.exports = config;