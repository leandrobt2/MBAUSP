-- Connect to the union_classification database
\c union_classification;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS union_classification;

-- Create tables
CREATE TABLE union_classification.Unions (
    union_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE union_classification.States (
    state_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    abbreviation CHAR(2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE union_classification.Cities (
    city_id SERIAL PRIMARY KEY,
    state_id INTEGER REFERENCES union_classification.States(state_id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE union_classification.Companies (
    company_id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL UNIQUE,
    corporate_name VARCHAR(255) NOT NULL,
    trading_name VARCHAR(255),
    primary_cnae VARCHAR(7) NOT NULL,
    city_id INTEGER REFERENCES union_classification.Cities(city_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE union_classification.Classifications (
    classification_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES union_classification.Companies(company_id),
    union_id INTEGER REFERENCES union_classification.Unions(union_id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'CONFIRMED', 'REJECTED')),
    confidence_score FLOAT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE union_classification.Admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_companies_cnpj ON union_classification.Companies(cnpj);
CREATE INDEX idx_classifications_status ON union_classification.Classifications(status);
CREATE INDEX idx_classifications_company ON union_classification.Classifications(company_id);
CREATE INDEX idx_cities_state ON union_classification.Cities(state_id);

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON union_classification.Companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classifications_updated_at
    BEFORE UPDATE ON union_classification.Classifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create initial admin user (password should be changed after first login)
INSERT INTO union_classification.Admins (username, password_hash, name, email)
VALUES ('admin', '$2b$10$your_hash_here', 'Admin User', 'admin@example.com');