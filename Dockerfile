# Use Python 3.9 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Create necessary directories with proper permissions
RUN mkdir -p uploads/games output keys static/css static/js templates \
    && touch uploads/.gitkeep output/.gitkeep keys/.gitkeep

# Expose port (update if your app uses a different port)
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]