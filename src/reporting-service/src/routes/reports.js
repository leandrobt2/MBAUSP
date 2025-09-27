const express = require('express');
const router = express.Router();
const { Parser } = require('json2csv');
const { getClassificationMetrics, getModelPerformanceMetrics } = require('../services/reportingService');
const { logger } = require('../utils/logger');

// Get classification metrics
router.get('/classifications', async (req, res) => {
  try {
    const { startDate, endDate, unionId, format } = req.query;
    
    const metrics = await getClassificationMetrics({
      startDate: new Date(startDate),
      endDate: new Date(endDate),
      unionId: unionId ? parseInt(unionId) : null
    });

    if (format === 'csv') {
      const parser = new Parser();
      const csv = parser.parse(metrics);
      
      res.header('Content-Type', 'text/csv');
      res.attachment('classification_metrics.csv');
      return res.send(csv);
    }

    res.json(metrics);
  } catch (error) {
    logger.error('Error getting classification metrics:', error);
    res.status(500).json({ error: 'Failed to get classification metrics' });
  }
});

// Get model performance metrics
router.get('/model-performance', async (req, res) => {
  try {
    const { startDate, endDate, format } = req.query;
    
    const metrics = await getModelPerformanceMetrics({
      startDate: new Date(startDate),
      endDate: new Date(endDate)
    });

    if (format === 'csv') {
      const parser = new Parser();
      const csv = parser.parse(metrics);
      
      res.header('Content-Type', 'text/csv');
      res.attachment('model_performance.csv');
      return res.send(csv);
    }

    res.json(metrics);
  } catch (error) {
    logger.error('Error getting model performance metrics:', error);
    res.status(500).json({ error: 'Failed to get model performance metrics' });
  }
});

module.exports = router;