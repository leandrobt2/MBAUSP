const sql = require('mssql');
const { logger } = require('../utils/logger');

const config = {
  user: process.env.DB_USER || 'sa',
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER || 'db',
  database: process.env.DB_NAME || 'UnionClassification',
  options: {
    encrypt: false,
    trustServerCertificate: true
  }
};

async function getClassificationMetrics({ startDate, endDate, unionId }) {
  try {
    const pool = await sql.connect(config);
    
    const result = await pool.request()
      .input('startDate', sql.DateTime2, startDate)
      .input('endDate', sql.DateTime2, endDate)
      .input('unionId', sql.Int, unionId)
      .query(`
        SELECT 
          c.classification_id,
          co.corporate_name,
          u.name as union_name,
          c.status,
          c.confidence_score,
          a.name as analyst_name,
          c.submitted_at,
          c.processed_at,
          DATEDIFF(MINUTE, c.submitted_at, c.processed_at) as processing_time_minutes
        FROM union_classification.Classifications c
        JOIN union_classification.Companies co ON c.company_id = co.company_id
        JOIN union_classification.Unions u ON c.union_id = u.union_id
        LEFT JOIN union_classification.Analysts a ON c.analyst_id = a.analyst_id
        WHERE c.submitted_at BETWEEN @startDate AND @endDate
        AND (@unionId IS NULL OR u.union_id = @unionId)
      `);

    return result.recordset;
  } catch (error) {
    logger.error('Database error:', error);
    throw error;
  }
}

async function getModelPerformanceMetrics({ startDate, endDate }) {
  try {
    const pool = await sql.connect(config);
    
    const result = await pool.request()
      .input('startDate', sql.DateTime2, startDate)
      .input('endDate', sql.DateTime2, endDate)
      .query(`
        WITH ModelPredictions AS (
          SELECT 
            c.classification_id,
            c.union_id as predicted_union_id,
            CASE 
              WHEN c.status = 'APPROVED' THEN 1
              ELSE 0
            END as correct_prediction
          FROM union_classification.Classifications c
          WHERE c.submitted_at BETWEEN @startDate AND @endDate
        )
        SELECT
          COUNT(*) as total_predictions,
          SUM(correct_prediction) as correct_predictions,
          CAST(SUM(correct_prediction) AS FLOAT) / COUNT(*) as accuracy,
          DATEPART(MONTH, c.submitted_at) as month,
          DATEPART(YEAR, c.submitted_at) as year
        FROM ModelPredictions mp
        JOIN union_classification.Classifications c ON mp.classification_id = c.classification_id
        GROUP BY DATEPART(MONTH, c.submitted_at), DATEPART(YEAR, c.submitted_at)
        ORDER BY year, month
      `);

    return result.recordset;
  } catch (error) {
    logger.error('Database error:', error);
    throw error;
  }
}

module.exports = {
  getClassificationMetrics,
  getModelPerformanceMetrics
};