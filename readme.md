# Hospital Backend System

This project is a backend system for a hospital, built with Django and Django REST Framework. It provides secure user management, patient–doctor assignment, doctor note submissions, and dynamic scheduling of actionable steps based on live LLM (Language Learning Model) processing. The system includes encryption of sensitive data, JWT authentication, and a distributed task queue using Celery and Redis. Additionally, API documentation is provided via Swagger UI, and the entire stack is containerized using Docker.

---

## Table of Contents

- [Hospital Backend System](#hospital-backend-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Architecture \& Design Decisions](#architecture--design-decisions)
    - [User Management \& Authentication](#user-management--authentication)
    - [Encryption \& Data Security](#encryption--data-security)
    - [Patient–Doctor Assignment](#patientdoctor-assignment)
    - [Doctor Notes \& LLM Integration](#doctor-notes--llm-integration)
    - [Dynamic Scheduling \& Reminders](#dynamic-scheduling--reminders)
    - [Data Storage](#data-storage)
    - [Containerization \& Deployment](#containerization--deployment)
  - [Installation \& Setup](#installation--setup)
  - [API Endpoints](#api-endpoints)
    - [User Management:](#user-management)
    - [Patient–Doctor Assignment:](#patientdoctor-assignment-1)
    - [Doctor's Patient List:](#doctors-patient-list)
    - [Doctor Notes \& Actionable Steps:](#doctor-notes--actionable-steps)
    - [Dynamic Scheduling \& Reminders:](#dynamic-scheduling--reminders-1)
    - [API Documentation (Swagger UI):](#api-documentation-swagger-ui)

---

## Features

- **User Management**
  - User signup (with name, email, password, and role selection: doctor or patient)
  - JWT authentication for secure API access
  - Password reset via email

- **Patient–Doctor Assignment**
  - Patients can view and select from a list of available doctors
  - Doctors can retrieve a list of patients assigned to them

- **Doctor Notes & Actionable Steps**
  - Doctors can submit encrypted notes for patients
  - Notes are processed by an LLM (using OpenAI API integration) to extract actionable steps (checklist and plan items)
  - Previously scheduled actionable steps are cancelled when a new note is submitted

- **Dynamic Scheduling & Reminders**
  - Reminders for plan items are scheduled via Celery and Redis
  - Reminders repeat daily until the patient checks in
  - A dedicated endpoint is provided for patients to "check in," stopping further reminders

- **API Documentation**
  - Swagger UI integration for interactive API documentation

- **Containerization**
  - Docker and Docker Compose setup for easy deployment and scalability

---

## Architecture & Design Decisions

### User Management & Authentication

- **Custom User Model:**  
  The project extends Django’s `AbstractUser` to include roles (doctor and patient) and uses a UUID as the primary key for enhanced security and non-guessability.

- **JWT Authentication:**  
  Authentication is implemented using Django REST Framework’s JWT (via SimpleJWT). This approach provides stateless, secure, and scalable authentication suitable for RESTful APIs.

### Encryption & Data Security

- **Sensitive Data Encryption:**  
  Patient notes are encrypted using Fernet (symmetric encryption provided by the `cryptography` library). This ensures that raw notes can only be decrypted and viewed by authorized parties (the patient and the doctor).

- **Environment-Based Secrets:**  
  Critical secrets like the encryption key and Django's `SECRET_KEY` are stored in a `.env` file and loaded via `django-environ` to keep them out of the source code.

### Patient–Doctor Assignment

- **Doctor Selection:**  
  Patients can choose from a list of available doctors, with the system storing the assignment in a dedicated model.

- **Doctor's Patient List:**  
  Doctors can easily retrieve their assigned patients using an API endpoint.

### Doctor Notes & LLM Integration

- **Doctor Note Submission:**  
  Doctors can submit notes that are encrypted upon storage. The encrypted data ensures privacy and data security.

- **LLM Integration:**  
  The system integrates with a live LLM (demonstrated here with OpenAI's GPT-3.5 API) to process the note and extract actionable steps. The API is called with a carefully designed prompt that instructs the model to return a JSON with immediate tasks (checklist) and scheduled actions (plan).

### Dynamic Scheduling & Reminders

- **Celery & Redis:**  
  Asynchronous tasks are managed by Celery using Redis as a message broker. Celery is used for scheduling reminders for plan items.

- **Repeating Reminders:**  
  A Celery task (`send_reminder`) is set up to re-schedule itself daily until the patient checks in. A dedicated API endpoint allows patients to "check in" and stop further reminders.

### Data Storage

- **Database:**  
  For demonstration purposes, SQLite is used. However, the project is designed to be database agnostic and can be configured to use PostgreSQL or any other relational database in production.

### Containerization & Deployment

- **Docker:**  
  The application is containerized using Docker. A single Dockerfile is provided to build the image, and Docker Compose orchestrates multiple services (web, celery, and redis).

- **Gunicorn:**  
  Gunicorn is used as the WSGI HTTP server for serving the Django application in production.

- **Entry Point Script:**  
  An entry point script is used to run migrations and collect static files when the web container starts, ensuring that the app is ready for production deployment.

---

## Installation & Setup

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd hospital_backend

2. **Create and Activate the Virtual Environment (using Pipenv):**

    ```bash
    Copy
    Edit
    pipenv --python 3.9
    pipenv shell
    pipenv install

3. **Configure Environment Variables:**

    Create a .env file in the project root with the following variables:

   ```bash
    DEBUG=True
    SECRET_KEY=your_secret_key_here
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_URL=sqlite:///db.sqlite3
    ENCRYPTION_KEY=Your32ByteBase64EncodedKey==
    CELERY_BROKER_URL=redis://redis:6379/0
    OPENAI_API_KEY=your_openai_api_key_here

4. **Run Migrations & Create a Superuser:**

   ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser

5. **Run the Development Server:**

   ```bash
   python manage.py runserver

6. **Run the Celery Worker (in a separate terminal):**

   ```bash
   celery -A hospital_backend worker --pool=solo -l info


## API Endpoints

### User Management:
- **Signup:** `POST /api/signup/`
- **Login:** `POST /api/token/` & `POST /api/token/refresh/`
- **Forgot Password:** `POST /api/forgot-password/` (sends an email with a password reset link)

### Patient–Doctor Assignment:
- **List Available Doctors:** `GET /api/doctors/`
- **Assign a Doctor:** `POST /api/assign/`

### Doctor's Patient List:
- **Retrieve Patients:** `GET /api/my-patients/`

### Doctor Notes & Actionable Steps:
- **Submit Note:** `POST /api/notes/`
- **Retrieve Actionable Steps:** `GET /api/steps/`

### Dynamic Scheduling & Reminders:
- **Check-In for Reminder:** `POST /api/check-in/<step_id>/`

### API Documentation (Swagger UI):
- **Available at:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
