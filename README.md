# The Daily Journalist 

A professional Django-based news management system. Follow these steps **strictly in order** to set up and run the application.

---

## 1. Step One: Clone the Project
First, bring the code from GitHub to your local machine.

1. **Open your terminal** (PowerShell or Git Bash).
2. **Clone the repository**:
   ```bash
   git clone [https://github.com/your-profile/news_application.git](https://github.com/your-profile/news_application.git)
Enter the directory:

Bash
cd news_application
2. Step Two: Local Environment Setup
Before configuring the database, you must set up your Python environment.

Create a Virtual Environment:

PowerShell
python -m venv .venv
Activate the Environment:

PowerShell: .\.venv\Scripts\Activate.ps1

CMD: .\.venv\Scripts\activate.bat

Install Dependencies:

PowerShell
pip install -r requirements.txt
3. Step Three: MySQL Database Creation
Crucial: You must create the database schema before running migrations or starting the app.

Open MySQL Workbench or the MySQL Command Line.

Run the following command:

SQL
CREATE DATABASE news_db;
4. Step Four: Configuration & Secrets
Locate the secrets_keys.txt file in the root folder.

Ensure your MYSQL_USER and MYSQL_PASSWORD in that file match your local MySQL credentials.

Open news_project/settings.py to verify the DATABASES section is pulling these secrets correctly.

5. Step Five: Database Migrations
Build the tables and apply the unique email constraints:

PowerShell
python manage.py makemigrations
python manage.py migrate
6. Step Six: Run the Application
Create a Superuser:

PowerShell
python manage.py createsuperuser
Start the Server:

PowerShell
python manage.py runserver
Access the site at: http://127.0.0.1:8000/

 Alternative: Docker Setup (Automated)
If you prefer using Docker, follow these steps after cloning the project:

Build and Start Containers:

PowerShell
docker-compose up -d --build
Run Migrations inside Docker:

PowerShell
docker-compose exec web python manage.py migrate