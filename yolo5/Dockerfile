FROM ultralytics/yolov5:v6.2-cpu
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN curl -L https://github.com/ultralytics/yolov5/releases/download/v6.2/yolov5s.pt -o yolov5s.pt

COPY . .

CMD ["python3", "app.py"]
