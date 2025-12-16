# Use a Python image with a smaller footprint
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies needed for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Create a 'templates' directory if it doesn't exist (it should)
RUN mkdir -p /app/templates

# Expose the port Flask runs on
EXPOSE 5000

# Run the application using Gunicorn (a production-ready WSGI server)
# The sentence transformer model will download on first run.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]