# Build stage for frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend/ ./
RUN npm run build

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY app/backend/ ./backend/

# Copy data and generated files
COPY data/ ./data/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Create .env template
RUN echo "# Configure these environment variables" > .env.docker

# Expose ports
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_MODE=local

# Start backend (frontend static files can be served by FastAPI or nginx)
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
