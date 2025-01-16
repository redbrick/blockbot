FROM python:3.12.7-alpine3.20

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src src

CMD ["python3", "-m", "src"]
