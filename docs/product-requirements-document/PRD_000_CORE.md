# Product Requirements Document (PRD)
## Automated Union Classification System

### 1. Introduction and Vision

**The Problem:** In Brazil, classifying a company with its correct labor union ("enquadramento sindical") is a legally mandated, high-stakes process governed by the Consolidation of Labor Laws (CLT). The principle of "unicidade sindical" (union uniqueness) prohibits multiple unions from representing the same professional category in the same geographic area, adding another layer of complexity. Today, this classification is performed manually by legal analysts or, worse, by entrepreneurs themselves, a method that is slow, inefficient, and prone to error. An incorrect classification can lead to significant legal liabilities, invalid collective bargaining agreements, and financial insecurity.

**Product Vision:** To create an intelligent, automated, and reliable platform that revolutionizes the union classification process. By leveraging machine learning, we will provide entrepreneurs with a fast and accurate classification, while empowering legal analysts to transition from manual data processors to expert validators. This system will serve as a definitive, efficient solution, reducing legal risk and operational friction for all stakeholders.

**Strategic Goals:**
* **Drastically Reduce Turnaround Time:** Cut the time from an entrepreneur's request to a final, validated classification.
* **Increase Classification Accuracy:** Minimize human error and ensure compliance with complex labor laws, thereby reducing legal and financial risks.
* **Boost Analyst Productivity:** Automate the initial classification to allow legal experts to focus their time on validation and handling complex edge cases, shifting their role from execution to oversight.
* **Build a Continuously Improving System:** Implement a human-in-the-loop feedback system where analyst corrections are used to perpetually retrain and improve the model's accuracy over time.

### 2. Personas

**a. The Entrepreneur / Applicant**
* **Profile:** An entrepreneur, founder, or administrative professional tasked with registering a new company and ensuring its legal compliance.
* **Needs:**
    * A straightforward, fast, and online method to determine their company's correct union affiliation.
    * A definitive and trustworthy result to avoid future legal complications.
    * To navigate the complexities of Brazilian labor legislation without needing to become an expert themselves.
* **Pain Points (Current Process):**
    * **Slowness & Bottlenecks:** The current semi-automated process is agonizingly slow, especially during peak periods of new company registrations.
    * **Uncertainty & Risk:** Making the classification themselves or relying on a potentially biased union's advice can lead to costly errors and legal challenges down the line.
    * **Lack of a Central Authority:** There is no official, federally regulated channel to request this service, leading to a fragmented and confusing process.

**b. The Legal Analyst (Federation Specialist)**
* **Profile:** A legal expert employed by a Labor Federation, responsible for ensuring the correct classification of companies within their jurisdiction.
* **Needs:**
    * A centralized dashboard to manage all pending classification requests.
    * Tools that streamline the verification of company data (CNAE codes, business activities, location).
    * High confidence in the data and suggestions to make swift, accurate decisions.
* **Pain Points (Current Process):**
    * **Repetitive Manual Labor:** The entire process of analyzing legal documents and cross-referencing information is done manually, which is tedious and inefficient.
    * **High Risk of Human Error:** Under the pressure of a high volume of requests, the risk of making a mistake with significant legal consequences is ever-present.
    * **Inconsistency:** Maintaining a consistent standard of classification across a large team and thousands of cases is a major challenge.

### 3. User Journeys

**a. Entrepreneur's Journey: Requesting a Classification**
1.  **Access:** The entrepreneur navigates to the system's public web portal.
2.  **Submission:** They fill out a simple, intuitive form with their company's data, including its primary and secondary CNAE codes, address (CEP), and other relevant details from their articles of incorporation.
3.  **Confirmation:** Upon submission, the system immediately displays a success message confirming their request has been received and is now in the processing queue.
4.  **Resolution:** Once the classification is validated by a legal analyst, the system automatically sends a formal email to the entrepreneur, clearly stating the correct union for their company.

**b. Legal Analyst's Journey: Validating a Suggestion**
1.  **Login:** The analyst logs into the secure admin web application.
2.  **Review Dashboard:** They are presented with a dashboard listing all pending classification requests. Crucially, each request is already populated with a **suggested union classification** generated by the Machine Learning model.
3.  **Detailed Analysis:** The analyst selects a case to review the company's full details alongside the model's suggestion.
4.  **Decision Point:**
    * **Scenario 1 (Approval):** If the AI's suggestion is correct, the analyst simply clicks an "Approve" button. The system finalizes the company-union link in the database.
    * **Scenario 2 (Correction):** If the suggestion is incorrect, the analyst uses a search/dropdown to select the correct union and saves the correction. This action not only finalizes the link but also flags the data point as a valuable correction for future model retraining.
5.  **Completion:** The decision triggers the notification email to the entrepreneur and makes the corrected data available for the next model training cycle.

### 4. Features

**Domain: Request Management (Applicant Portal)**
* **`FUNC-01: Company Data Submission Form`**
    * **Description:** A public-facing web form for entrepreneurs to submit their company's data for classification analysis.
    * **Acceptance Criteria:**
        * Must capture key predictive features like primary/secondary CNAE, city, and zip code.
        * Must include field validation to ensure data quality and integrity.
        * Upon submission, the user must receive immediate on-screen feedback confirming receipt.

* **`FUNC-02: Automated Email Notification`**
    * **Description:** An automated service that informs the applicant of their final, validated union classification via email.
    * **Acceptance Criteria:**
        * The email must be triggered automatically the moment an analyst finalizes a classification.
        * The email content must be clear, professional, and state the definitive union affiliation.

**Domain: Analysis & Validation (Analyst Portal)**
* **`FUNC-03: Pending Classifications Dashboard`**
    * **Description:** A secure, role-based administrative interface for legal analysts.
    * **Acceptance Criteria:**
        * Must require user authentication for access.
        * Must display a real-time list of all companies awaiting validation.
        * The list must prominently feature the ML model's suggested union for each case, allowing for quick assessment.

* **`FUNC-04: Classification Validation Screen`**
    * **Description:** The core workspace where an analyst approves or corrects a model's suggestion.
    * **Acceptance Criteria:**
        * Must display all relevant company data alongside the model's prediction.
        * Must provide a single-click "Approve" action.
        * Must provide an intuitive interface (e.g., a searchable dropdown) for overriding the suggestion with the correct union.
        * The final decision must be permanently recorded in the database.

**Domain: Classification Intelligence (Machine Learning Engine)**
* **`FUNC-05: Automated Classification Suggestion`**
    * **Description:** The core ML process that predicts the union for a newly submitted company.
    * **Acceptance Criteria:**
        * The process must be triggered automatically for every new company saved in the database.
        * The model must generate a prediction (a suggested union ID).
        * This suggestion must be stored and linked to the company record to be displayed on the analyst's dashboard.

* **`FUNC-06: Human-in-the-Loop Retraining Cycle`**
    * **Description:** An MLOps pipeline that leverages validated and corrected classifications from analysts to continuously retrain and improve the predictive model.
    * **Acceptance Criteria:**
        * The system must have a mechanism to periodically gather all newly validated/corrected classifications as a fresh training dataset.
        * A process (automated or triggered) must exist to initiate model retraining using this new data.
        * The newly trained model's performance must be evaluated, and if it meets or exceeds the current model's metrics, it should be promoted to production. This entire lifecycle must be tracked in MLflow.

### 5. Success Metrics

* **Core Model Performance:** Maintain or exceed the pilot study's optimized **F1-score of 0.82**. This will be the primary measure of the model's accuracy and reliability.
* **Suggestion Approval Rate:** The percentage of ML suggestions approved by analysts without any changes. **Target: >80%** within three months of launch. This metric directly measures the model's real-world usefulness.
* **Cycle Time Reduction:** The average time from submission to final notification. **Target: Reduce by 90%** compared to the manual baseline.
* **Analyst Throughput:** The number of classifications a single analyst can process per day. **Target: Increase by 5x**.