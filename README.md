# The Daily Journalist

A professional Django-based news application featuring user subscriptions, article management, and journalist creation of articles and newsletters

# Prerequisites
* Python 3.11+
* MySQL Server
* Docker (Optional for containerization)

# Setup with Virtual Environment (venv)
**Create the Virtual Environment:**
   Open PowerShell in the project root and run:
   ```powershell
   python -m venv .venv

Activate the Environment:
PowerShell
.\.venv\Scripts\Activate.ps1

Install Dependencies:
Ensure your requirements.txt is in the folder, then run:
PowerShell
pip install -r requirements.txt

Set up the Database:
Ensure your MySQL server is running and the credentials in settings.py match your local setup (see secrets.txt). Then run:
PowerShell
python manage.py migrate

Start the Development Server:
PowerShell
python manage.py runserver
Access the app at: http://127.0.0.1:8000



# RUN DOCKER
Build the Docker Image:
Open your terminal in the project root (where the Dockerfile is located) and run:

PowerShell
docker build -t the-daily-journalist .
Run the Container:

PowerShell
docker run -p 8000:8000 the-daily-journalist
Database Connectivity:
The application is configured to connect to your local MySQL host using host.docker.internal. Ensure your MySQL service is configured to allow connections from the Docker bridge network.

Access the app at: http://localhost:8000

 Documentation
Documentation is generated using Sphinx and can be found in the docs/ directory.
To view the HTML documentation, open:
docs/build/html/index.html



1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "News Application"

## Setup Secrets
The application requires sensitive credentials to run (Secret Key and Email Password).
1. Open the included `secrets.txt` file.
2. You can either:
   - Set these as environment variables on your system.
   - Or, temporarily paste them into the `settings.py` file in the fields labeled `os.environ.get`.   