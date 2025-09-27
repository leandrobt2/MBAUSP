const fs = require('fs').promises;
const path = require('path');
const Handlebars = require('handlebars');

const TEMPLATES_DIR = path.join(__dirname, '../templates');

async function loadTemplate(templateName) {
  try {
    const templatePath = path.join(TEMPLATES_DIR, `${templateName}.hbs`);
    const templateContent = await fs.readFile(templatePath, 'utf8');
    return Handlebars.compile(templateContent);
  } catch (error) {
    throw new Error(`Failed to load template ${templateName}: ${error.message}`);
  }
}

module.exports = {
  loadTemplate
};