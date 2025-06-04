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
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent

import stock_crawler as crawler
import os
import re

app = Flask(__name__)

# ✅ LINE 憑證
LINE_CHANNEL_ACCESS_TOKEN = '+WI3XRv9qqjsZ01k3ZAzqGcPCWIDntzDJtGHNgQ5ixo57CReF67hfZIkw5KifwLlQuk32ZX8h1o932gDqXUSobnln7ng2BERDDe4LhpalFd9aIa0dL8JSF97y55aGxH24QQiDSxJXJyTSyC520F3KgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a3bce23c40fac99c653686f3944ce4c0'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ 提供圖片靜態服務
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(crawler.IMAGE_OUTPUT_FOLDER, filename, mimetype='image/png')

@app.route("/", methods=["GET"])
def index():
    return "LINE Stock Bot is running."

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# ✅ 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            parts = msg.split()
            if len(parts) == 1 and parts[0].isdigit():
                # 基本 K 線查詢
                path = crawler.generate_kline_image(parts[0])
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            elif len(parts) == 2 and parts[1].lower() == 'now':
                # 即時價格查詢
                info = crawler.get_realtime_price(parts[0])
                reply = TextMessage(text=info)

            elif len(parts) == 3 and re.match(r'\d{4}-\d{2}-\d{2}', parts[1]) and re.match(r'\d{4}-\d{2}-\d{2}', parts[2]):
                # 區間查詢
                path = crawler.generate_kline_image_by_date(parts[0], parts[1], parts[2])
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            elif msg.lower() == '幫助':
                reply = TextMessage(text="📌 指令範例：\n2330 → 查近月K線\n2330 now → 即時股價\n2330 2024-01-01 2024-02-01 → 區間走勢")

            else:
                reply = TextMessage(text="⚠️ 指令錯誤！請輸入『幫助』查看可用指令")

        except Exception as e:
            reply = TextMessage(text=f"❌ 發生錯誤：{e}")

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        )
        line_bot_api.reply_message(req)

# ✅ 好友加入時歡迎訊息
@handler.add(FollowEvent)
def handle_follow(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        welcome = TextMessage(text=(
            "👋 歡迎加入！這是股票資訊查詢機器人～\n\n"
            "📌 查詢範例：\n"
            "2330 → 查近月K線\n"
            "2330 now → 即時股價\n"
            "2330 2024-01-01 2024-04-01 → 區間走勢\n"
            "輸入『幫助』查看更多指令"
        ))

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[welcome]
        )
        line_bot_api.reply_message(req)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
