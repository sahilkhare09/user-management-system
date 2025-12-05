🎉 User Management System – FastAPI

A modern, scalable, and cleanly architected User Management System built using FastAPI, featuring authentication, organisation/department management, Excel import, and application logging.

🔖 Badges
<p align="left"> <img src="https://img.shields.io/badge/Python-3.12-blue" /> <img src="https://img.shields.io/badge/FastAPI-0.110+-teal" /> <img src="https://img.shields.io/badge/Framework-FastAPI-green" /> <img src="https://img.shields.io/badge/License-MIT-yellow.svg" /> <img src="https://img.shields.io/badge/Build-Passing-brightgreen" /> <img src="https://img.shields.io/badge/Status-Active-success" /> </p>
✨ Features

🔐 Authentication System

User registration

Login using JWT access & refresh tokens

Refresh token expiry: 2 days

Password hashing with bcrypt

🏢 Organisation Management

Create, update, delete organisations

Link departments and users

🏬 Department Management

CRUD operations for departments

📥 Excel Import System

Import bulk users/departments from .xlsx files

Uses openpyxl for parsing

Smart validation & error handling

📝 Logging System

File-based logs stored inside logs/

View logs using API routes

🧱 Clean Architecture

Routers → Services → Models → Schemas

Fully modular and scalable

📁 Project Structure
user_management_system/
│
├── app/
│   ├── core/
│   │   ├── config.py               # App settings & environment variables
│   │   ├── security.py             # JWT auth utilities
│   │   └── __init__.py
│   │
│   ├── database/
│   │   ├── db.py                   # Database engine/session
│   │   └── __init__.py
│   │
│   ├── logs/                       # Application log files
│   │
│   ├── migrations/                 # Alembic migration files (if used)
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── organisation.py
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── department_router.py
│   │   ├── import_router.py
│   │   ├── log_router.py
│   │   └── organisation_router.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── department.py
│   │   ├── organisation.py
│   │   ├── logs.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── department_service.py
│   │   ├── import_service.py
│   │   ├── log_service.py
│   │   └── organisation_service.py
│   │
│   ├── utils/
│   │   ├── excel_importer.py       # Excel parsing and import logic
│   │   ├── hash.py                 # Password hashing utilities
│   │   └── logger.py               # Logging handler
│   │
│   ├── main.py                     # FastAPI entry point
│   └── __init__.py
│
├── .env                            # Environment config
├── requirements.txt                # Dependencies
├── README.md                       # Documentation
└── .gitignore                      # Ignore sensitive/unnecessary files

⚙️ Environment Variables (.env)
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=2

🛠️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/yourusername/user_management_system.git
cd user_management_system

2️⃣ Create & activate virtual environment
python -m venv venv
source venv/bin/activate   # Linux/MacOS
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Start the FastAPI server
uvicorn app.main:app --reload

5️⃣ API Documentation
Swagger UI → http://127.0.0.1:8000/docs
ReDoc      → http://127.0.0.1:8000/redoc

📌 Example API Requests
🔐 Register User

POST /auth/register

{
  "full_name": "Sahil Khare",
  "email": "sahil@example.com",
  "password": "StrongPassword123",
  "department_id": 1
}

🔑 Login

POST /auth/login

{
  "email": "sahil@example.com",
  "password": "StrongPassword123"
}

♻️ Refresh Token

POST /auth/refresh

{
  "refresh_token": "your-refresh-token"
}

🏢 Create Organisation

POST /organisation/

{
  "name": "Tech Corp",
  "address": "Mumbai, India",
  "description": "Software company"
}

🏬 Create Department

POST /department/

{
  "name": "Human Resources",
  "organisation_id": 1
}

📥 Excel Import

POST /import/excel
Send as form-data:

file: users.xlsx

📬 Postman Collection Documentation
🧰 Create a Postman Environment
Variable	Value
base_url	http://127.0.0.1:8000
access_token	(auto-filled after login)

Set Authorization:

Type → Bearer Token  
Token → {{access_token}}

📁 Postman Folder Structure
Authentication

POST /auth/register

POST /auth/login

POST /auth/refresh

Organisation

GET /organisation/

POST /organisation/

PUT /organisation/{id}

DELETE /organisation/{id}

Department

GET /department/

POST /department/

PUT /department/{id}

DELETE /department/{id}

Excel Import

POST /import/excel

Logs

GET /logs/

📄 License

This project is licensed under the MIT License.

🤝 Contributing

Pull requests are welcome.
Please open an issue before making major changes.