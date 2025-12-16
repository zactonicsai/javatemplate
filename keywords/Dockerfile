FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install FastText from source
WORKDIR /tmp
RUN git clone https://github.com/facebookresearch/fastText.git && \
    cd fastText && \
    make && \
    pip install .

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic

# Create app directory
WORKDIR /app

# Copy application files
COPY server.py /app/
COPY requirements.txt /app/

# Create directories for models and data
RUN mkdir -p /app/models /app/data

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
