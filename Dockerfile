# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
