# Stage 1: Build the frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
# Use --link for faster copying if supported, otherwise standard COPY is fine
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python backend
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the SentenceTransformer model to avoid download during runtime
# This makes the image larger but the startup much faster and more reliable
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"

# Copy the rest of the application
# We do this AFTER installing requirements to leverage Docker cache
COPY . .

# Copy the built frontend from the previous stage
# Make sure the directory exists
RUN mkdir -p /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port Railway uses
EXPOSE 8080

# Environment variable for the port (Railway provides PORT)
ENV PORT=8080

# Start the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
