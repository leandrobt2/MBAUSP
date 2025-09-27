const amqp = require('amqplib');
const config = require('../config');
const logger = require('./logger');

let channel;

async function initializeQueue() {
    try {
        const connection = await amqp.connect(config.rabbitmq.url);
        channel = await connection.createChannel();

        // Assert queues
        await channel.assertQueue(config.rabbitmq.queues.notifications, { durable: true });
        await channel.assertQueue(config.rabbitmq.queues.modelRetraining, { durable: true });

        logger.info('RabbitMQ connection established');
    } catch (error) {
        logger.error('Failed to connect to RabbitMQ:', error);
        throw error;
    }
}

async function publishNotification(notification) {
    try {
        await channel.sendToQueue(
            config.rabbitmq.queues.notifications,
            Buffer.from(JSON.stringify(notification)),
            { persistent: true }
        );
        logger.info(`Notification queued: ${notification.type}`);
    } catch (error) {
        logger.error('Failed to publish notification:', error);
        throw error;
    }
}

async function triggerModelRetraining(data) {
    try {
        await channel.sendToQueue(
            config.rabbitmq.queues.modelRetraining,
            Buffer.from(JSON.stringify(data)),
            { persistent: true }
        );
        logger.info('Model retraining triggered');
    } catch (error) {
        logger.error('Failed to trigger model retraining:', error);
        throw error;
    }
}

module.exports = {
    initializeQueue,
    publishNotification,
    triggerModelRetraining
};