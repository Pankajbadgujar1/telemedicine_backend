Telemedicine Backend API
A simple Django REST API for telemedicine appointments with doctors and patients.
What's Inside

User registration and login (Doctors & Patients)
JWT authentication for security
Appointment booking system
Doctor online/offline status
PostgreSQL database

Before You Start
Make sure you have these installed:

Python 3.8+
PostgreSQL
Postman (for testing)

Quick Setup
1. Get the Code
bashmkdir telemedicine-backend
cd telemedicine-backend
Copy all the project files into this folder.
2. Setup Python Environment
bash# Create virtual environment
python -m venv env

# Turn it on (Windows)
env\Scripts\activate

# Install packages
pip install -r requirements.txt
3. Setup Database
Start PostgreSQL:

Open Windows Services
Find PostgreSQL service and start it

Create database:
bashpsql -U postgres
CREATE DATABASE telemedicine_db;
\q
4. Configure Settings
Create .env file and add:
DB_NAME=telemedicine_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
5. Setup Database Tables
bashpython manage.py makemigrations
python manage.py migrate
6. Start the Server
bashpython manage.py runserver
Your API is now running at: http://127.0.0.1:8000
Testing with Postman
Import Collection

Open Postman
Click "Import"
Select the Telemedicine_API_Collection.postman_collection.json file
Done!

Test Flow
Step 1: Register a Doctor

Go to "Authentication" → "Register User"
Use this data:

json{
    "name": "Dr. Smith",
    "email": "doctor@test.com",
    "username": "drsmith",
    "password": "Test123!",
    "password_confirm": "Test123!",
    "role": "doctor"
}

Click Send

Step 2: Register a Patient

Go to "Authentication" → "Register Patient"
Use this data:

json{
    "name": "John Patient",
    "email": "patient@test.com",
    "username": "johnpatient",
    "password": "Test123!",
    "password_confirm": "Test123!",
    "role": "patient"
}

Click Send

Step 3: Login as Doctor

Go to "Authentication" → "Login"
Use:

json{
    "email": "doctor@test.com",
    "password": "Test123!"
}

Click Send (token saves automatically)

Step 4: Set Doctor Online

Go to "Doctor Status" → "Update Doctor Status"
Use:

json{
    "is_online": true
}

Click Send

Step 5: Login as Patient

Go to "Authentication" → "Login"
Use patient credentials
Click Send

Step 6: Book Appointment

Go to "Appointments" → "Create Appointment"
Use:

json{
    "doctor": 1,
    "appointment_date": "2024-12-25T10:00:00Z",
    "reason": "Checkup"
}

Click Send

Step 7: View Appointments

Login as doctor again
Go to "Appointments" → "Get All Appointments"
Click Send to see all appointments

API Quick Reference
Authentication

POST /api/auth/register/ - Register new user
POST /api/auth/login/ - Login user
GET /api/auth/profile/ - Get user profile

Doctor Status

POST /api/auth/doctor/status/ - Update online status
GET /api/auth/doctor/{id}/status/ - Check doctor status

Appointments

POST /api/appointments/create/ - Create appointment (patients)
GET /api/appointments/ - List appointments
PATCH /api/appointments/{id}/update/ - Update appointment
DELETE /api/appointments/{id}/cancel/ - Cancel appointment

Common Issues
Database connection error?

Make sure PostgreSQL is running
Check your .env file password

Module not found error?

Activate virtual environment: env\Scripts\activate
Install packages: pip install -r requirements.txt

Token not working in Postman?

Re-login to get fresh token
Check collection variables are set

Can't access some endpoints?

Make sure you're logged in as the right user type
Patients can only create appointments
Doctors can confirm appointments

File Structure
telemedicine-backend/
├── manage.py
├── requirements.txt
├── .env
├── telemedicine/          # Main settings
├── core/                  # User management
├── appointments/          # Appointment system
└── README.md
What Each App Does
Core App:

Handles user registration/login
Manages doctor and patient accounts
JWT token authentication
Doctor online/offline status

Appointments App:

Appointment booking
Status tracking (pending → confirmed → completed)
Doctor appointment management

Database Models
User:

Name, email, password
Role (doctor or patient)
Created date

Appointment:

Patient and doctor info
Date and time
Status and reason
Notes

Doctor Status:

Online/offline status
Last seen time

Security Features

Passwords are encrypted
JWT tokens for authentication
Role-based permissions
Input validation
SQL injection protection

