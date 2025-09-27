const jwt = require('jsonwebtoken');
const config = require('../config');
const logger = require('../services/logger');

function authenticate(req, res, next) {
    try {
        const authHeader = req.headers.authorization;
        
        if (!authHeader) {
            return res.status(401).json({ error: 'Authorization header missing' });
        }

        const token = authHeader.split(' ')[1];
        if (!token) {
            return res.status(401).json({ error: 'Token missing' });
        }

        const decoded = jwt.verify(token, config.jwt.secret);
        req.user = decoded;
        
        next();
    } catch (error) {
        logger.error('Authentication error:', error);
        return res.status(401).json({ error: 'Invalid token' });
    }
}

function authorize(roles = []) {
    return (req, res, next) => {
        try {
            if (!req.user) {
                return res.status(401).json({ error: 'User not authenticated' });
            }

            if (roles.length && !roles.includes(req.user.role)) {
                return res.status(403).json({ error: 'Insufficient permissions' });
            }

            next();
        } catch (error) {
            logger.error('Authorization error:', error);
            return res.status(403).json({ error: 'Authorization failed' });
        }
    };
}

module.exports = {
    authenticate,
    authorize
};