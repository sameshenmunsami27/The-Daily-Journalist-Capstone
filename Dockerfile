# Use Python 3.12 (The 'Preferred' version for Django 6.0+)
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the directory inside the container
WORKDIR /app

#  Install system dependencies for MySQL 
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

#  Install Python libraries
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project code into the container
COPY . /app/

# Open port 8000 for Django
EXPOSE 8000

# Start the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]