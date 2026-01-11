FROM python:3.10-slim

WORKDIR /app

# 1️⃣ Install dependencies first (cached forever unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 2️⃣ Copy code separately (this layer changes often)
COPY code/ ./code/
COPY data/ ./data/

CMD ["python", "code/main.py"]
