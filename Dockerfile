# Base image with Python 3.12 (slim version for smaller size)
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are shown in real time (important for Docker logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for some Python packages
# (e.g. gcc for compiling native extensions)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port the FastAPI app will run on
EXPOSE 8000

# Run migrations and start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]