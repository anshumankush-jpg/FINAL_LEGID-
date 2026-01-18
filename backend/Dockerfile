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
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy artillery module
COPY artillery/ ./artillery/

# Copy application code
COPY app/ ./app/

# Copy data directory if it exists (for vector store)
# Create necessary directories
RUN mkdir -p ./data/docs ./data/faiss ./data/history ./data/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port (Cloud Run uses $PORT)
EXPOSE 8000

# Health check with longer start period for cold starts
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application with increased timeout for cold starts
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 120

