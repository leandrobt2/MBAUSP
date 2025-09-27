-- Create Database
CREATE DATABASE UnionClassification;
GO

USE UnionClassification;
GO

-- Create Schemas
CREATE SCHEMA union_classification;
GO

-- Create Tables
CREATE TABLE union_classification.Cities (
    city_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    state_code CHAR(2) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE union_classification.CNAEs (
    cnae_id VARCHAR(10) PRIMARY KEY,
    description NVARCHAR(255) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE union_classification.Unions (
    union_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    jurisdiction_city_id INT,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Unions_Cities FOREIGN KEY (jurisdiction_city_id) REFERENCES union_classification.Cities(city_id)
);

CREATE TABLE union_classification.Companies (
    company_id INT IDENTITY(1,1) PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL UNIQUE,
    corporate_name NVARCHAR(255) NOT NULL,
    trading_name NVARCHAR(255),
    primary_cnae_id VARCHAR(10) NOT NULL,
    city_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Companies_CNAEs FOREIGN KEY (primary_cnae_id) REFERENCES union_classification.CNAEs(cnae_id),
    CONSTRAINT FK_Companies_Cities FOREIGN KEY (city_id) REFERENCES union_classification.Cities(city_id)
);

CREATE TABLE union_classification.CompanySecondaryCNAEs (
    company_id INT,
    cnae_id VARCHAR(10),
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT PK_CompanySecondaryCNAEs PRIMARY KEY (company_id, cnae_id),
    CONSTRAINT FK_CompanySecondaryCNAEs_Companies FOREIGN KEY (company_id) REFERENCES union_classification.Companies(company_id),
    CONSTRAINT FK_CompanySecondaryCNAEs_CNAEs FOREIGN KEY (cnae_id) REFERENCES union_classification.CNAEs(cnae_id)
);

CREATE TABLE union_classification.Analysts (
    analyst_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE union_classification.Classifications (
    classification_id INT IDENTITY(1,1) PRIMARY KEY,
    company_id INT NOT NULL,
    union_id INT NOT NULL,
    status NVARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    confidence_score DECIMAL(5,4),
    analyst_id INT,
    analyst_notes NVARCHAR(MAX),
    submitted_at DATETIME2 DEFAULT GETDATE(),
    processed_at DATETIME2,
    CONSTRAINT FK_Classifications_Companies FOREIGN KEY (company_id) REFERENCES union_classification.Companies(company_id),
    CONSTRAINT FK_Classifications_Unions FOREIGN KEY (union_id) REFERENCES union_classification.Unions(union_id),
    CONSTRAINT FK_Classifications_Analysts FOREIGN KEY (analyst_id) REFERENCES union_classification.Analysts(analyst_id)
);

CREATE TABLE union_classification.Notifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    classification_id INT NOT NULL,
    type NVARCHAR(50) NOT NULL,
    status NVARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'SENT', 'FAILED')),
    recipient_email NVARCHAR(255) NOT NULL,
    template_name NVARCHAR(100) NOT NULL,
    retry_count INT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    sent_at DATETIME2,
    CONSTRAINT FK_Notifications_Classifications FOREIGN KEY (classification_id) REFERENCES union_classification.Classifications(classification_id)
);

CREATE TABLE union_classification.AuditLogs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    entity_type NVARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    actor_id INT,
    changes NVARCHAR(MAX),
    ip_address NVARCHAR(45),
    created_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_AuditLogs_Analysts FOREIGN KEY (actor_id) REFERENCES union_classification.Analysts(analyst_id)
);

-- Create Indexes
CREATE INDEX IX_Companies_CNPJ ON union_classification.Companies(cnpj);
CREATE INDEX IX_Classifications_Status ON union_classification.Classifications(status);
CREATE INDEX IX_Classifications_SubmittedAt ON union_classification.Classifications(submitted_at);
CREATE INDEX IX_Notifications_Status ON union_classification.Notifications(status);
CREATE INDEX IX_AuditLogs_EntityType_EntityId ON union_classification.AuditLogs(entity_type, entity_id);

-- Create Triggers for Audit Logging
CREATE TRIGGER union_classification.TR_Classifications_Audit
ON union_classification.Classifications
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO union_classification.AuditLogs (entity_type, entity_id, action, actor_id, changes)
    SELECT 
        'Classification',
        i.classification_id,
        'INSERT',
        i.analyst_id,
        (SELECT * FROM inserted WHERE classification_id = i.classification_id FOR JSON PATH)
    FROM inserted i
    UNION ALL
    SELECT 
        'Classification',
        d.classification_id,
        'DELETE',
        d.analyst_id,
        (SELECT * FROM deleted WHERE classification_id = d.classification_id FOR JSON PATH)
    FROM deleted d
    WHERE NOT EXISTS (SELECT 1 FROM inserted WHERE classification_id = d.classification_id);
END;
GO

-- Create Views for Reporting
CREATE VIEW union_classification.vw_ClassificationMetrics AS
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
LEFT JOIN union_classification.Analysts a ON c.analyst_id = a.analyst_id;
GO