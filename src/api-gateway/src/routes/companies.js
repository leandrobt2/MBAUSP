const db = require('../services/database');
const logger = require('../services/logger');
const queue = require('../services/queue');
const { validateCompanyData } = require('../utils/validation');

async function create(req, res, next) {
    try {
        const companyData = req.body;

        // Validate input data
        const validationErrors = validateCompanyData(companyData);
        if (validationErrors) {
            return res.status(400).json({ errors: validationErrors });
        }

        // Check for duplicate CNPJ
        const existingCompany = await db.query(
            'SELECT company_id FROM union_classification.Companies WHERE cnpj = @cnpj',
            { cnpj: companyData.cnpj }
        );

        if (existingCompany.length > 0) {
            return res.status(409).json({ error: 'Company already exists' });
        }

        // Save company data
        const [company] = await db.query(`
            INSERT INTO union_classification.Companies (
                cnpj, corporate_name, trading_name, primary_cnae_id, city_id
            ) VALUES (
                @cnpj, @corporateName, @tradingName, @primaryCnae, @cityId
            )
            OUTPUT INSERTED.*
        `, {
            cnpj: companyData.cnpj,
            corporateName: companyData.corporateName,
            tradingName: companyData.tradingName,
            primaryCnae: companyData.primaryCnae,
            cityId: companyData.cityId
        });

        // Request ML classification
        const mlResponse = await fetch(`${config.services.mlEngine}/predict/${company.company_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(companyData)
        }).then(r => r.json());

        // Save initial classification
        await db.query(`
            INSERT INTO union_classification.Classifications (
                company_id, union_id, status, confidence_score
            ) VALUES (
                @companyId, @unionId, 'PENDING', @confidence
            )
        `, {
            companyId: company.company_id,
            unionId: mlResponse.suggested_union_id,
            confidence: mlResponse.confidence_score
        });

        // Queue confirmation notification
        await queue.publishNotification({
            type: 'SUBMISSION_RECEIVED',
            recipientEmail: companyData.email,
            data: {
                companyName: companyData.corporateName,
                trackingId: company.company_id
            }
        });

        res.status(201).json({
            message: 'Company registration successful',
            trackingId: company.company_id
        });

    } catch (error) {
        next(error);
    }
}

async function get(req, res, next) {
    try {
        const { id } = req.params;

        const [company] = await db.query(`
            SELECT 
                c.*,
                cl.status as classification_status,
                cl.union_id,
                u.name as union_name
            FROM union_classification.Companies c
            LEFT JOIN union_classification.Classifications cl ON c.company_id = cl.company_id
            LEFT JOIN union_classification.Unions u ON cl.union_id = u.union_id
            WHERE c.company_id = @id
        `, { id });

        if (!company) {
            return res.status(404).json({ error: 'Company not found' });
        }

        res.json(company);
    } catch (error) {
        next(error);
    }
}

module.exports = {
    create,
    get
};