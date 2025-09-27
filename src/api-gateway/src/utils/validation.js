const Joi = require('joi');

function validateCompanyData(data) {
    const schema = Joi.object({
        cnpj: Joi.string()
            .pattern(/^\d{14}$/)
            .required()
            .messages({
                'string.pattern.base': 'CNPJ must be exactly 14 digits'
            }),
        corporateName: Joi.string()
            .min(3)
            .max(255)
            .required(),
        tradingName: Joi.string()
            .min(3)
            .max(255)
            .allow(null),
        primaryCnae: Joi.string()
            .pattern(/^\d{7}$/)
            .required()
            .messages({
                'string.pattern.base': 'Primary CNAE must be exactly 7 digits'
            }),
        cityId: Joi.number()
            .integer()
            .positive()
            .required(),
        email: Joi.string()
            .email()
            .required()
    });

    const { error } = schema.validate(data, { abortEarly: false });
    return error ? error.details.map(detail => detail.message) : null;
}

function validateClassificationInput(data) {
    const schema = Joi.object({
        unionId: Joi.number()
            .integer()
            .positive()
            .required(),
        status: Joi.string()
            .valid('PENDING', 'CONFIRMED', 'REJECTED')
            .required(),
        notes: Joi.string()
            .max(1000)
            .allow(null)
    });

    const { error } = schema.validate(data, { abortEarly: false });
    return error ? error.details.map(detail => detail.message) : null;
}

module.exports = {
    validateCompanyData,
    validateClassificationInput
};