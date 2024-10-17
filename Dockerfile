FROM python:3.9-slim

# Install SQLite version >= 3.35.0
RUN apt-get update && apt-get install -y sqlite3

# Install your Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app files
COPY . /app
WORKDIR /app

# Run the Streamlit app
CMD ["streamlit", "run", "rag_app.py"]
