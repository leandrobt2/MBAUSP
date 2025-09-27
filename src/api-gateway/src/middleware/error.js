const logger = require('../services/logger');

function errorHandler(err, req, res, next) {
    logger.error('Unhandled error:', err);

    if (err.type === 'ValidationError') {
        return res.status(400).json({
            error: 'Validation Error',
            details: err.details
        });
    }

    if (err.type === 'NotFoundError') {
        return res.status(404).json({
            error: 'Resource Not Found',
            message: err.message
        });
    }

    if (err.type === 'DuplicateError') {
        return res.status(409).json({
            error: 'Duplicate Resource',
            message: err.message
        });
    }

    // Default error
    res.status(500).json({
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'An unexpected error occurred'
    });
}

module.exports = errorHandler;