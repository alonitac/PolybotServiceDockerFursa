FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]