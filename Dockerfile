# Stage 1: Build the frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
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

# Install Torch CPU specifically to save ~5GB of space
# This is the most important step for Railway's 4GB limit
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download a smaller but still very high-quality model 
# 'all-MiniLM-L6-v2' is ~80MB, whereas 'all-mpnet-base-v2' is ~450MB.
# We will stick to your requested model but ensure it's CPU-only.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"

# Copy the rest of the application
COPY . .

# Copy built frontend
RUN mkdir -p /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose port
EXPOSE 8080
ENV PORT=8080

# Start
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
