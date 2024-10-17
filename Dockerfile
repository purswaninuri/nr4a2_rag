FROM python:3.9-slim

# Install the required SQLite version
RUN apt-get update && apt-get install -y sqlite3

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set up the application
COPY . /app
WORKDIR /app

# Run the Streamlit app
CMD ["streamlit", "run", "rag_app.py"]
