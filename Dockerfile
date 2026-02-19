# 1. Use Python 3.11
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and enable real-time logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the directory inside the container
WORKDIR /app

# 4. Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python libraries
# We will generate this requirements.txt file in the next step
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your project code into the container
COPY . /app/

# 7. Open port 8000 for Django
EXPOSE 8000

# 8. Start the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]