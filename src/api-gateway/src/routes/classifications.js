const express = require('express');
const router = express.Router();

// Company classification request
router.post('/companies', async (req, res) => {
    try {
        const { companyData } = req.body;
        
        // 1. Validate input data
        await validateCompanyData(companyData);
        
        // 2. Save company data
        const company = await saveCompanyData(companyData);
        
        // 3. Request ML classification
        const mlResponse = await requestClassification(company.id);
        
        // 4. Save preliminary classification
        await savePreliminaryClassification({
            companyId: company.id,
            unionId: mlResponse.suggestedUnionId,
            confidenceScore: mlResponse.confidenceScore,
            status: 'PENDING'
        });

        // 5. Send response
        res.status(201).json({
            message: 'Classification request received',
            trackingId: company.id,
            estimatedTime: '24 hours'
        });

        // 6. Queue notification
        await queueNotification({
            type: 'SUBMISSION_RECEIVED',
            companyId: company.id,
            email: companyData.email
        });

    } catch (error) {
        console.error('Error processing company request:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get pending classifications
router.get('/classifications/pending', async (req, res) => {
    try {
        const pendingClassifications = await db.query(`
            SELECT 
                c.classification_id,
                co.corporate_name,
                co.cnpj,
                co.primary_cnae_id,
                c.union_id as suggested_union_id,
                c.confidence_score,
                c.submitted_at
            FROM Classifications c
            JOIN Companies co ON c.company_id = co.company_id
            WHERE c.status = 'PENDING'
            ORDER BY c.submitted_at ASC
        `);

        res.json(pendingClassifications);
    } catch (error) {
        console.error('Error fetching pending classifications:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Approve classification
router.post('/classifications/:id/approve', async (req, res) => {
    try {
        const { id } = req.params;
        const { analystId } = req.body;

        // 1. Update classification status
        await db.query(`
            UPDATE Classifications
            SET status = 'APPROVED',
                analyst_id = @analystId,
                processed_at = GETDATE()
            WHERE classification_id = @id
        `);

        // 2. Create company-union link
        await createCompanyUnionLink(id);

        // 3. Queue notification
        await queueNotification({
            type: 'CLASSIFICATION_APPROVED',
            classificationId: id
        });

        // 4. Trigger model retraining
        await triggerModelRetraining();

        res.json({ message: 'Classification approved successfully' });
    } catch (error) {
        console.error('Error approving classification:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;