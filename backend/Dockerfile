# Stage 1: Base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 5000

# Set the command to run the application
# We use Gunicorn, a production-ready WSGI server.
# 'run:app' refers to the 'app' instance created in the 'run.py' file.
# We set the FLASK_CONFIG to 'production' to use production settings.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-e", "FLASK_CONFIG=production", "run:app"]
