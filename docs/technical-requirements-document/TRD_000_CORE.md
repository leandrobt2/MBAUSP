# Technical Requirements Document (TRD)
## Automated Union Classification System

### 1. Architectural Vision

The system will be built on a **composable, microservices-based architecture**, containerized with Docker and orchestrated via Docker Compose[cite: 57, 76]. This approach was chosen to directly address the key architectural drivers identified in the source study:
* **Scalability:** Allows individual services to scale independently based on demand[cite: 58].
* **Resilience:** Isolates services so that the failure of one component (e.g., the `Mailer`) does not cascade and bring down the entire system[cite: 74, 75].
* **Maintainability:** Avoids a rigid monolithic structure, allowing for easier updates, independent deployments, and technology stack evolution for each service[cite: 59, 60].
* **CI/CD Efficiency:** Smaller, independent services lead to faster build and test cycles in continuous integration pipelines[cite: 70].

All inter-service communication will be handled via synchronous, stateless **RESTful APIs**, adhering to standard principles like Client-Server separation and a Uniform Interface[cite: 61, 63, 64].

### 2. Architectural Components & Domains

**a. Web Application Domain**
* **Container: `WebApp-Frontend`**
    * **Technology:** HTML5, CSS3, JavaScript.
    * **Responsibility:** Renders the public-facing submission form for entrepreneurs.
    * **Communication:** Makes REST API calls to the `API-Gateway`.

* **Container: `WebApp-Admin`**
    * **Technology:** HTML5, CSS3, JavaScript (potentially a framework like React or Vue for a richer UI).
    * **Responsibility:** Renders the secure admin dashboard for legal analysts.
    * **Communication:** Makes REST API calls to the `API-Gateway` for data retrieval and updates.

* **Container: `API-Gateway`**
    * **Technology:** Python (FastAPI or Flask).
    * **Responsibility:** Acts as the single entry point for both frontend applications. Exposes a consolidated REST API and forwards requests to the appropriate backend services. Manages concerns like authentication for the admin panel.
    * **Example Endpoints:**
        * `POST /empresas`: Registers a new company[cite: 66].
        * `GET /enquadramentos/pendentes`: Lists pending classifications for the admin panel.
        * `POST /enquadramentos/{id}/aprovar`: Approves a classification.

**b. Machine Learning Domain**
* **Container: `ML-Engine`**
    * **Component: `MLflow Lifecycle Manager`**
        * **Technology:** MLflow.
        * **Responsibility:** Manages the entire MLOps lifecycle, including tracking experiments, logging parameters and metrics (precision, recall, F1-score), versioning models, and managing the model registry (staging, production)[cite: 104, 105, 106, 107].
    * **Component: `Prediction-API`**
        * **Technology:** Python (Flask), Scikit-learn, XGBoost, Pandas[cite: 51, 52].
        * **Responsibility:** Exposes a single, highly optimized REST endpoint (e.g., `POST /enquadramento/{empresa_id}`) for real-time inference[cite: 67]. It loads the current production model from the MLflow registry to make predictions.
    * **Component: `Training-Service`**
        * **Technology:** Python, NumPy, Pandas, Scikit-learn[cite: 51].
        * **Responsibility:** A service or scheduled job that executes the model retraining pipeline. It queries the database for new validated data, applies the necessary preprocessing steps (data cleaning, SMOTE), trains a new model, evaluates it, and registers it in MLflow.

**c. Persistence Domain**
* **Container: `Database`**
    * **Technology:** MS-SQL Server[cite: 77].
    * **Responsibility:** Provides persistent storage for all system data.
    * **Data Model:** Will strictly follow the Entity-Relationship Diagram from the study, with tables for `SINDICATOS`, `EMPRESAS`, and `CNAES`, linked by foreign keys to ensure referential integrity[cite: 43, 48].

**d. Notification Domain**
* **Container: `Mailer-Service`**
    * **Technology:** Python with an SMTP library. This is a prime candidate for a **Serverless** implementation (e.g., AWS Lambda, Google Cloud Function) to optimize cost and operational overhead, as it's an event-driven, low-frequency task[cite: 72].
    * **Responsibility:** Handles the sending of transactional emails to applicants.
    * **Communication:** Triggered via an API call from the `API-Gateway` upon successful classification validation.

### 3. Data Pipeline and Model Strategy

A critical component of this system is the data preprocessing strategy, which was proven to be the key to achieving high model accuracy. The `Training-Service` must implement the following steps:
1.  **Data Ingestion:** Fetch all validated classifications from the `Database`.
2.  **Data Cleaning:** Implement a filtering step to remove records belonging to unions with a very low number of samples (e.g., fewer than 10 occurrences). This was a crucial step in the study to reduce noise from extreme minority classes[cite: 238].
3.  **Data Balancing:** Apply the **Synthetic Minority Over-sampling Technique (SMOTE)** to the cleaned dataset[cite: 187, 189]. This technique generates synthetic samples for minority classes, creating a balanced dataset for training and mitigating the model's bias towards majority classes. This step was directly responsible for improving the F1-score from a baseline of ~0.48 to 0.82[cite: 261, 243].
4.  **Training & Evaluation:** Train the chosen model (e.g., XGBoost with Grid Search optimization) on the preprocessed data and evaluate its performance using multiclass metrics, with a focus on the weighted and macro F1-scores[cite: 211, 175].

### 4. Non-Functional Requirements (NFRs)

* **Performance:**
    * **Inference Latency:** The P95 latency for the `Prediction-API` must be **< 800 milliseconds**, as benchmarked on an **AWS EC2 t3.medium** instance or equivalent[cite: 249, 55].
    * **UI Response Time:** All API calls supporting the `WebApp-Admin` must respond in under 1 second to ensure a fluid user experience.
* **Scalability:**
    * Each microservice must be stateless and horizontally scalable. The architecture should support running multiple instances of the `Prediction-API` behind a load balancer to handle high request volumes.
* **Security:**
    * The `WebApp-Admin` and its backing API endpoints must be protected by a robust authentication/authorization mechanism (e.g., JWT).
    * All sensitive data, such as database credentials and API keys, must be managed via environment variables or a secrets management service, not hardcoded in the source code.
* **Monitoring & Observability:**
    * **ML Model Monitoring:** MLflow is mandatory for tracking model performance over time. Dashboards should be set up to monitor for model drift and degradation in F1-score, precision, and recall[cite: 107].
    * **System Health:** All services must produce structured logs (e.g., JSON format). A centralized logging solution (e.g., ELK Stack, Datadog) should be implemented to aggregate logs and monitor the health and performance (CPU, memory, latency) of each container.

### 5. Technical Acceptance Criteria

* All services must be fully containerized with their own `Dockerfile`.
* A `docker-compose.yml` file must exist at the project root to deploy the entire stack for local development and testing with a single `docker-compose up` command.
* All REST APIs must be documented using the OpenAPI (Swagger) specification.
* The codebase must include automated unit and integration tests, with a CI pipeline that runs these tests on every commit.
* A load test script must be created to validate that the `Prediction-API` meets the <800ms latency NFR under a simulated load.
* The development environment and dependencies must be documented, specifying Python 3.12.4 and the libraries listed in the study (e.g., scikit-learn, pandas, numpy, etc.)[cite: 50, 51, 52].