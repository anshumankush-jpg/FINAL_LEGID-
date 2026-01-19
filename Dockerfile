# Combined Dockerfile for Cloud Run deployment
# Builds both Angular frontend and Python backend

# ============================================
# Stage 1: Build Angular Frontend
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files
COPY frontend/package*.json ./

# Install all dependencies (including dev) with legacy peer deps
RUN npm ci --legacy-peer-deps

# Copy source code
COPY frontend/ .

# Build the Angular application for production
RUN npm run build -- --configuration=production

# ============================================
# Stage 2: Python Backend with Frontend static files
# ============================================
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker cache optimization)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# CPU-only PyTorch (prevents huge CUDA/NVIDIA wheels - saves ~2GB)
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app/ ./app/

# Copy artillery module if exists
COPY backend/artillery/ ./artillery/ 2>/dev/null || true

# Copy frontend build output to serve as static files
# Vite outputs to dist/ by default
COPY --from=frontend-builder /frontend/dist ./static/

# Create necessary directories
RUN mkdir -p ./data/docs ./data/faiss ./data/history ./data/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV SERVE_STATIC=true

# Expose port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 120
