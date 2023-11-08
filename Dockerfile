FROM python:3.10.13-alpine3.18

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]