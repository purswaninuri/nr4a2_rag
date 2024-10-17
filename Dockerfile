# Use the official Python slim image
FROM python:3.9-slim

# Install system dependencies including SQLite and PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    postgresql-client \
    gcc

# Set environment variables to avoid issues with system-level prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . /app
WORKDIR /app

# Run the Streamlit app
CMD ["streamlit", "run", "rag_app.py"]
