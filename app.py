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

LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_SECRET'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
                # 特定區間查詢
                path = crawler.generate_kline_image_by_date(parts[0], parts[1], parts[2])
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            elif msg.lower() == '幫助':
                reply = TextMessage(text="輸入股票代號查K線圖\n例如：2330\n輸入 2330 now 查即時價\n輸入 2330 2024-01-01 2024-04-01 查特定期間")
            else:
                reply = TextMessage(text="⚠️ 指令錯誤！請輸入『幫助』查看可用指令")

        except Exception as e:
            reply = TextMessage(text=f"❌ 發生錯誤：{e}")

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply]
        )
        line_bot_api.reply_message(req)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
