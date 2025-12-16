FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Build FastText C++ executable from source
WORKDIR /tmp
#RUN git clone https://github.com/facebookresearch/fastText.git && \
COPY src .
COPY requirements.txt .
RUN make && \
    cp fasttext /usr/local/bin/ && \
    chmod +x /usr/local/bin/fasttext 

# Verify FastText is installed
#RUN ls -l  fasttext --help

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Create app directory
WORKDIR /app

# Copy application files
COPY server.py /app/
COPY requirements.txt /app/
COPY index.html /app/static/

# Create directories for models and data
RUN mkdir -p /app/models /app/data /app/temp

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000","--log-level", "debug"]
