FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]