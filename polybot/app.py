import flask
from flask import request
import os
from bot import ObjectDetectionBot

app = flask.Flask(__name__)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']
BUCKET_NAME = os.environ['BUCKET_NAME']
YOLO5_SERVICE_URL = os.environ['YOLO5_SERVICE_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL, BUCKET_NAME, YOLO5_SERVICE_URL)

    app.run(host='0.0.0.0', port=8443, ssl_context=('bot_cert.pem','bot_key.pem'))
