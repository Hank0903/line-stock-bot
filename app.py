from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ApiClient,
    TextMessage,
    ImageMessage,
)
from linebot.v3.messaging.models import ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import stock_crawler as crawler
import os

app = Flask(__name__)

# LINE 金鑰設定
LINE_CHANNEL_ACCESS_TOKEN = '+WI3XRv9qqjsZ01k3ZAzqGcPCWIDntzDJtGHNgQ5ixo57CReF67hfZIkw5KifwLlQuk32ZX8h1o932gDqXUSobnln7ng2BERDDe4LhpalFd9aIa0dL8JSF97y55aGxH24QQiDSxJXJyTSyC520F3KgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a3bce23c40fac99c653686f3944ce4c0'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def index():
    return "The server is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    print("Received signature:", signature)
    print("Request body:", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ InvalidSignatureError: Channel Secret 錯誤或請求被修改")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if msg.lower() == '幫助':
            reply = TextMessage(text="輸入股票代號查K線圖\n例如：2330\n輸入 2330 info 查股價\n輸入 2330 sma 查均線")
        elif msg.isdigit():
            path = crawler.generate_kline_image(msg)
            image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
            reply = ImageMessage(original_content_url=image_url, preview_image_url=image_url)
        elif 'info' in msg:
            stock_id = msg.split()[0]
            info = crawler.get_stock_info(stock_id)
            reply = TextMessage(text=info)
        elif 'sma' in msg:
            stock_id = msg.split()[0]
            path = crawler.generate_kline_image(stock_id, show_sma=True)
            image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
            reply = ImageMessage(original_content_url=image_url, preview_image_url=image_url)
        else:
            reply = TextMessage(text="請輸入股票代號或輸入『幫助』查看指令")

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        )
        line_bot_api.reply_message(req)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
