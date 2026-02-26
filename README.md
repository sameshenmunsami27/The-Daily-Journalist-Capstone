# The Daily Journalist - Capstone Project

A full-stack Django news application featuring user authentication, article management, and a session-based shopping cart with automated invoicing.

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

1. Clone the Repository
Bash
git clone https://github.com/sameshenmunsami27/The-Daily-Journalist-Capstone.git
cd The-Daily-Journalist-Capstone

2. Set Up a Virtual Environment
PowerShell
# Create the environment
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

3. Install Dependencies
PowerShell
pip install -r requirements.txt

4. Configuration (Secrets & Environment Variables)
Create a file named secrets_keys.txt in the root directory and add your credentials:
If needed my secret_keys.txt file is attached containing this information

Plaintext
DJANGO_SECRET_KEY=your_secret_key
MYSQL_DATABASE=news_db
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_app_password

5. Database Setup (MySQL)
Ensure your MySQL server is running and the database is created. Then, run the migrations:

PowerShell
python manage.py makemigrations
python manage.py migrate

6. Create a Superuser
To access the Journalist and Editor dashboards, you must create an administrative account. In this application, the Superuser is granted both Journalist and Editor privileges automatically.

PowerShell
python manage.py createsuperuser
Follow the prompts in your terminal to set a username, email, and password.

Superuser Username: Enter your superuser user-name
Superuser Password: #IMPORTANT: This section asks you to enter your password however the password characters will not appear in the terminal.
Superuser email: You will need to provide a valid email address.
Once registered you will get a success message

7. Run the Application
PowerShell
python manage.py runserver
Access the application at http://127.0.0.1:8000/.