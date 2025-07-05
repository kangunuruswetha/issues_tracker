FROM python:3.11-buster

WORKDIR /app

COPY requirements.txt .
# NEW LINE: Install build-essential for system dependencies (e.g., for bcrypt)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# This CMD is overridden by docker-compose.yml, but keeping it clean
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]