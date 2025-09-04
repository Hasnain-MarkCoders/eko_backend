# Use official Python image
FROM python:3.11-slim

# Create non-root user early
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements with correct ownership
COPY --chown=app:app requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files with correct ownership
COPY --chown=app:app . .

# Switch to non-root user for security
USER app

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
