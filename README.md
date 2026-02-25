# The Daily Journalist - Capstone Project

A full-stack Django news application featuring user authentication, article management, and a session-based shopping cart with automated invoicing.

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd The-Daily-Journalist-Capstone
2. Set Up a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

#2. Set up a Virtual Environment
PowerShell
python -m venv venv
# Activate on Windows:
.\venv\Scripts\activate

#3. Install Dependencies
PowerShell
pip install -r requirements.txt


#4. Configuration (Secrets & Environment Variables)
This project uses a secrets_keys.txt file for sensitive credentials.

Create a file named secrets_keys.txt in the root directory (next to manage.py).

Add the following keys with your specific values:

DJANGO_SECRET_KEY=

MYSQL_DATABASE=news_db

MYSQL_USER=

MYSQL_PASSWORD=

EMAIL_USER=

EMAIL_PASSWORD=

#5. Database Setup (MySQL)
Ensure your MySQL server is running and you have created the database specified in your secrets file. Then, run the migrations:

PowerShell
python manage.py makemigrations
python manage.py migrate


#6. Run the Application
PowerShell
python manage.py runserver
Access the application at http://127.0.0.1:8000/.