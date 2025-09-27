const db = require('../services/database');
const logger = require('../services/logger');

async function getClassificationStats(req, res, next) {
    try {
        const stats = await db.query(`
            SELECT 
                u.name as union_name,
                COUNT(cl.classification_id) as total_classifications,
                COUNT(CASE WHEN cl.status = 'CONFIRMED' THEN 1 END) as confirmed,
                COUNT(CASE WHEN cl.status = 'PENDING' THEN 1 END) as pending,
                COUNT(CASE WHEN cl.status = 'REJECTED' THEN 1 END) as rejected,
                AVG(cl.confidence_score) as avg_confidence_score
            FROM union_classification.Classifications cl
            JOIN union_classification.Unions u ON cl.union_id = u.union_id
            GROUP BY u.union_id, u.name
            ORDER BY total_classifications DESC
        `);

        res.json(stats);
    } catch (error) {
        next(error);
    }
}

async function getRegionalDistribution(req, res, next) {
    try {
        const distribution = await db.query(`
            SELECT 
                s.name as state,
                c.name as city,
                COUNT(comp.company_id) as company_count,
                STRING_AGG(DISTINCT u.name, ', ') as unions
            FROM union_classification.Companies comp
            JOIN union_classification.Cities c ON comp.city_id = c.city_id
            JOIN union_classification.States s ON c.state_id = s.state_id
            JOIN union_classification.Classifications cl ON comp.company_id = cl.company_id
            JOIN union_classification.Unions u ON cl.union_id = u.union_id
            WHERE cl.status = 'CONFIRMED'
            GROUP BY s.state_id, s.name, c.city_id, c.name
            ORDER BY s.name, c.name
        `);

        res.json(distribution);
    } catch (error) {
        next(error);
    }
}

async function getConfidenceAnalysis(req, res, next) {
    try {
        const analysis = await db.query(`
            SELECT 
                u.name as union_name,
                AVG(CASE WHEN cl.status = 'CONFIRMED' THEN cl.confidence_score END) as avg_confirmed_confidence,
                AVG(CASE WHEN cl.status = 'REJECTED' THEN cl.confidence_score END) as avg_rejected_confidence,
                MIN(cl.confidence_score) as min_confidence,
                MAX(cl.confidence_score) as max_confidence
            FROM union_classification.Classifications cl
            JOIN union_classification.Unions u ON cl.union_id = u.union_id
            GROUP BY u.union_id, u.name
            HAVING COUNT(cl.classification_id) >= 10
            ORDER BY avg_confirmed_confidence DESC
        `);

        res.json(analysis);
    } catch (error) {
        next(error);
    }
}

async function getTimelineAnalysis(req, res, next) {
    try {
        const timeline = await db.query(`
            SELECT 
                FORMAT(cl.created_at, 'yyyy-MM') as month,
                COUNT(cl.classification_id) as total_classifications,
                COUNT(CASE WHEN cl.status = 'CONFIRMED' THEN 1 END) as confirmed,
                COUNT(CASE WHEN cl.status = 'REJECTED' THEN 1 END) as rejected,
                AVG(cl.confidence_score) as avg_confidence
            FROM union_classification.Classifications cl
            GROUP BY FORMAT(cl.created_at, 'yyyy-MM')
            ORDER BY month DESC
        `);

        res.json(timeline);
    } catch (error) {
        next(error);
    }
}

module.exports = {
    getClassificationStats,
    getRegionalDistribution,
    getConfidenceAnalysis,
    getTimelineAnalysis
};