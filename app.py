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
LINE_CHANNEL_ACCESS_TOKEN = '+WI3XRv9qqjsZ01k3ZAzqGcPCWIDntzDJtGHNgQ5ixo57CReF67hfZIkw5KifwLlQuk32ZX8h1o932gDqXUSobnln7ng2BERDDe4LhpalFd9aIa0dL8JSF97y55aGxH24QQiDSxJXJyTSyC520F3KgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a3bce23c40fac99c653686f3944ce4c0'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ 靜態檔案路由（用於讓 LINE 可以讀到圖片）
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

    # 使用正則判斷是否包含查詢天數
    match = re.match(r'(\d{4,5})\s*(\d+)?\s*(info|sma)?', msg)
    stock_id, days, command = match.groups() if match else (None, None, None)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        msgParts = msg.split()
        if len(msgParts) == 3 and re.match(r'^\d{4}-\d{2}-\d{2}$', msgParts[1]) and re.match(r'^\d{4}-\d{2}-\d{2}$', msgParts[2]):
            stock_id = msgParts[0]
            startDate = msgParts[1]
            endDate = msgParts[2]
            # stock_id, startDate, endDate = msgParts
            path = crawler.generate_kline_image_by_date(stock_id, startDate, endDate)
            image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
            reply = ImageMessage(original_content_url=image_url, preview_image_url=image_url)
        elif msg.lower() == '幫助':
            reply = TextMessage(text="輸入股票代號查K線圖\n例如：2330\n輸入 2330 info 查股價\n輸入 2330 sma 查均線\n"
                                     "輸入 2330 60 查近 60 天資料\n輸入 2330 sma 90 查 90 天均線\n輸入 2330 2024-01-01 2024-04-01 查特定區間")
        elif stock_id and stock_id.isdigit():
            try:
                days = int(days) if days else 30  # 預設 30 天
                path = crawler.generate_kline_image(stock_id, days, show_sma=(command == 'sma'))
                image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=image_url, preview_image_url=image_url)
            except Exception as e:
                reply = TextMessage(text=f"產生圖表失敗：{e}")
        elif 'info' in msg:
            info = crawler.get_stock_info(stock_id)
            reply = TextMessage(text=info)
        else:
            reply = TextMessage(text="請輸入股票代號或輸入『幫助』查看指令")

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        )
        line_bot_api.reply_message(req)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
