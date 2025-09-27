const express = require('express');
const router = express.Router();
const { sendEmail } = require('../services/emailService');
const { logger } = require('../utils/logger');

// Get notification status
router.get('/:id', async (req, res) => {
  try {
    // TODO: Implement notification status retrieval from database
    res.json({ id: req.params.id, status: 'pending' });
  } catch (error) {
    logger.error('Error getting notification status:', error);
    res.status(500).json({ error: 'Failed to get notification status' });
  }
});

// Manually trigger a notification (for testing/resend)
router.post('/trigger', async (req, res) => {
  try {
    const { to, templateName, data } = req.body;
    
    await sendEmail({ to, templateName, data });
    
    res.status(200).json({ message: 'Notification triggered successfully' });
  } catch (error) {
    logger.error('Error triggering notification:', error);
    res.status(500).json({ error: 'Failed to trigger notification' });
  }
});

module.exports = router;