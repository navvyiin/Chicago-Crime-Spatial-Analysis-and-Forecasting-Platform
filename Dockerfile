# ------------------------------------------------------------
# Base image: Python 3.13
# ------------------------------------------------------------
FROM python:3.13-slim

# ------------------------------------------------------------
# System dependencies for geospatial stack
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Environment variables for GDAL
# ------------------------------------------------------------
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_DATA=/usr/share/gdal

# ------------------------------------------------------------
# Application setup
# ------------------------------------------------------------
WORKDIR /app

# Install Python dependencies first (Docker cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# ------------------------------------------------------------
# Expose Gunicorn port
# ------------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------------
# Start Dash app via Gunicorn
# ------------------------------------------------------------
CMD ["gunicorn", "run_app:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
