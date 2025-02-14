# Dockerfile
FROM python:3.12-slim

# Prevent Python from writing pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    netcat-openbsd \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN pip install --upgrade pip pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /code/

# Install dependencies
RUN pipenv install --system --deploy

# Copy the rest of the application code
COPY . /code/

# Expose port 8000
EXPOSE 8000

# Default command (for web service, overridden in docker-compose for celery)
CMD ["gunicorn", "hospital_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
