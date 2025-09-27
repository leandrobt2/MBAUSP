const nodemailer = require('nodemailer');
const { logger } = require('../utils/logger');
const { loadTemplate } = require('../utils/templates');

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: process.env.SMTP_PORT === '465',
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
});

async function sendEmail({ to, templateName, data }) {
  try {
    // Load and compile email template
    const template = await loadTemplate(templateName);
    const { subject, html } = template(data);

    // Send email
    const info = await transporter.sendMail({
      from: process.env.SMTP_FROM,
      to,
      subject,
      html
    });

    logger.info(`Email sent successfully: ${info.messageId}`);
    return info;
  } catch (error) {
    logger.error('Failed to send email:', error);
    throw error;
  }
}

module.exports = {
  sendEmail
};