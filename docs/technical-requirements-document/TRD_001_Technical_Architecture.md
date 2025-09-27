# Technical Requirements Document – System Architecture

## Overview
This system automates union classification via ML models and microservices. It is designed with a **Composable Architecture** for scalability, maintainability, and modular evolution.

## Core Services
- **Frontend Web App (React/Next.js)**: Public and admin interfaces.
- **Ingestion API (Node.js/.NET)**: Handles submissions, validation, persistence.
- **MLFlow Service (Python, MLflow)**: Exposes trained models as REST APIs.
- **Admin API (Node.js/.NET)**: Backend for legal analyst operations.
- **Notification Service (Serverless / AWS Lambda)**: Email delivery and retries.
- **Database (MS SQL Server)**: Central relational storage.

## Data Model (Simplified ERD)
- **Company**: id, cnpj, name, cnae, city_id, submission_date
- **Union**: id, name, jurisdiction, city_id
- **Classification**: id, company_id, union_id, status, analyst_id, confidence
- **Analyst**: id, name, role, permissions
- **AuditLog**: id, entity, action, timestamp, actor_id

## Integrations
- MLFlow for predictions (REST).
- SMTP/email service for notifications.
- Authentication provider (OAuth2/JWT).

## Design Patterns
- **CQRS**: Separate read/write for admin reporting vs ingestion.
- **Event-Driven**: Notifications triggered via message queue (e.g., RabbitMQ/Kafka).
- **API Gateway**: Single entry point for external clients.

## Non-Functional Requirements
- **Performance**: < 800ms ML prediction response.
- **Security**: TLS 1.3, encrypted DB at rest, RBAC on APIs.
- **Scalability**: Independent scaling per service.
- **Resilience**: Circuit breakers, retries, fallback strategies.
- **Monitoring**: Prometheus metrics, Grafana dashboards, ELK logging.
- **Maintainability**: Versioned APIs, code linting, automated CI/CD pipelines.

## Technical Acceptance Criteria
- All APIs expose Swagger/OpenAPI docs.
- Each microservice includes health-check and readiness endpoints.
- All DB migrations tracked and reversible.
- Automated tests ≥ 80% coverage.
- CI/CD pipeline must deploy to staging before production.
