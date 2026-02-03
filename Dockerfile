# Stage 1: Build the frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the frontend
RUN npm run build

# Stage 2: Setup the backend and serve
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if needed (e.g. for sqlite)
# RUN apt-get update && apt-get install -y ...

# Copy backend requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Remove the frontend source directory from the backend image to keep it clean (optional)
# But we MUST copy the built assets from the previous stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port
EXPOSE 8000

# Command to run the application using uvicorn
# We also run the data loading script before starting the server to ensure DB is populated
CMD ["sh", "-c", "python storage/load_csv_to_sqlite.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
