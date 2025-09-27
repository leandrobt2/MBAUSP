const sql = require('mssql');
const config = require('../config');
const logger = require('./logger');

let pool;

async function initializeDatabase() {
    try {
        pool = await sql.connect(config.database.url);
        logger.info('Database connection established');
    } catch (error) {
        logger.error('Failed to connect to database:', error);
        throw error;
    }
}

async function query(sqlQuery, params = {}) {
    try {
        const request = pool.request();
        
        // Add parameters to the request
        Object.keys(params).forEach(key => {
            request.input(key, params[key]);
        });
        
        const result = await request.query(sqlQuery);
        return result.recordset;
    } catch (error) {
        logger.error('Database query error:', error);
        throw error;
    }
}

async function transaction(callback) {
    const transaction = new sql.Transaction(pool);
    
    try {
        await transaction.begin();
        await callback(transaction);
        await transaction.commit();
    } catch (error) {
        await transaction.rollback();
        throw error;
    }
}

module.exports = {
    initializeDatabase,
    query,
    transaction
};