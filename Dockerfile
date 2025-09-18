# Dockerfile - Streamlit + FAISS + SentenceTransformers image
# Builds the FAISS index at image build time so the container is ready-to-serve.

FROM python:3.11-slim

# --- System dependencies required for some Python packages (faiss, BLAS, torch backend) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libgomp1 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy pip requirements first for cached installs
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install Python deps
RUN python -m pip install --upgrade pip setuptools wheel
# Use --no-cache-dir to shrink image
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

# Ensure index and preference directories exist and have correct permissions
RUN mkdir -p /app/index /app/preference /app/data

# If you want the index to be built at image build time (faster container start),
# run the indexer now. This will download the sentence-transformers model during build.
# If you prefer to build at runtime, remove this RUN line and build in entrypoint.
RUN python -m search.indexer

# Expose Streamlit default port
EXPOSE 8501

# Environment variables for Streamlit to run headless and accessible
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Use a non-root user if you prefer (optional)
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Entrypoint: start Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]