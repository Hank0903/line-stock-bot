from flask import Flask, request, abort, send_from_directory
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
import re

app = Flask(__name__)

# LINE 金鑰設定
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_SECRET'

configuration = Configuration(access_token='+WI3XRv9qqjsZ01k3ZAzqGcPCWIDntzDJtGHNgQ5ixo57CReF67hfZIkw5KifwLlQuk32ZX8h1o932gDqXUSobnln7ng2BERDDe4LhpalFd9aIa0dL8JSF97y55aGxH24QQiDSxJXJyTSyC520F3KgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a3bce23c40fac99c653686f3944ce4c0')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(crawler.IMAGE_OUTPUT_FOLDER, filename, mimetype='image/png')

@app.route("/", methods=["GET"])
def index():
    return "The server is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()
    msg_parts = msg.split()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            if len(msg_parts) == 3 and re.match(r'\d{4}-\d{2}-\d{2}', msg_parts[1]) and re.match(r'\d{4}-\d{2}-\d{2}', msg_parts[2]):
                stock_id, start_date, end_date = msg_parts
                path = crawler.generate_kline_image_by_date(stock_id, start_date, end_date)
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            elif msg.lower() in ['幫助', 'help']:
                reply = TextMessage(text=(
                    "📈 股票查詢指令：\n"
                    "▶︎ 2330 → 查近 30 天K線圖\n"
                    "▶︎ 2330 60 → 查近 60 天K線圖\n"
                    "▶︎ 2330 sma → 查近 30 天均線圖\n"
                    "▶︎ 2330 sma 90 → 查近 90 天均線圖\n"
                    "▶︎ 2330 info → 查最新股價資訊\n"
                    "▶︎ 2330 2024-01-01 2024-04-01 → 查指定區間K線圖"
                ))

            else:
                match = re.match(r'(\d{4,5})(?:\s+(sma|info|\d+))?(?:\s+(\d+))?', msg.lower())
                if match:
                    stock_id, arg1, arg2 = match.groups()
                    command = None
                    days = 30

                    if arg1 == 'info':
                        command = 'info'
                    elif arg1 == 'sma':
                        command = 'sma'
                        days = int(arg2) if arg2 else 30
                    elif arg1 and arg1.isdigit():
                        days = int(arg1)

                    if command == 'info':
                        text = crawler.get_stock_info(stock_id)
                        reply = TextMessage(text=text)
                    else:
                        path = crawler.generate_kline_image(stock_id, days, show_sma=(command == 'sma'))
                        url = f"{crawler.IMAGE_HOST_URL}/{path}"
                        reply = ImageMessage(original_content_url=url, preview_image_url=url)
                else:
                    reply = TextMessage(text="❗請輸入有效指令，輸入『幫助』查看用法")

        except Exception as e:
            reply = TextMessage(text=f"❌ 發生錯誤：{str(e)}")

        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        ))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
