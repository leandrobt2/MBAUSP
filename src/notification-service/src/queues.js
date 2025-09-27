const amqp = require('amqplib');
const { sendEmail } = require('./services/emailService');
const { logger } = require('./utils/logger');

const QUEUE_NAME = 'notification_queue';

let channel;

async function setupQueues() {
  try {
    const connection = await amqp.connect(process.env.RABBITMQ_URL);
    channel = await connection.createChannel();
    
    await channel.assertQueue(QUEUE_NAME, {
      durable: true
    });

    // Start consuming messages
    channel.consume(QUEUE_NAME, handleNotification, {
      noAck: false
    });

    logger.info('RabbitMQ connection established');
  } catch (error) {
    logger.error('Failed to connect to RabbitMQ:', error);
    throw error;
  }
}

async function handleNotification(msg) {
  try {
    const notification = JSON.parse(msg.content.toString());
    
    logger.info(`Processing notification for classification ${notification.classificationId}`);
    
    await sendEmail({
      to: notification.recipientEmail,
      templateName: notification.templateName,
      data: notification.data
    });

    // Acknowledge the message
    channel.ack(msg);
    
    logger.info(`Successfully processed notification for classification ${notification.classificationId}`);
  } catch (error) {
    logger.error('Error processing notification:', error);
    
    // Requeue the message if it hasn't been retried too many times
    if (msg.fields.redelivered) {
      channel.nack(msg, false, false); // Don't requeue
    } else {
      channel.nack(msg, false, true); // Requeue
    }
  }
}

module.exports = {
  setupQueues
};