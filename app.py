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

# ✅ 請換成你的實際金鑰
LINE_CHANNEL_ACCESS_TOKEN = '+WI3XRv9qqjsZ01k3ZAzqGcPCWIDntzDJtGHNgQ5ixo57CReF67hfZIkw5KifwLlQuk32ZX8h1o932gDqXUSobnln7ng2BERDDe4LhpalFd9aIa0dL8JSF97y55aGxH24QQiDSxJXJyTSyC520F3KgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a3bce23c40fac99c653686f3944ce4c0'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ✅ 讓 LINE 可讀圖片
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(crawler.IMAGE_OUTPUT_FOLDER, filename, mimetype='image/png')

@app.route("/", methods=["GET"])
def index():
    return "✅ LINE Stock Bot is running."

# ✅ webhook 入口
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ 簽名驗證失敗")
        abort(400)
    except Exception as e:
        print(f"❌ webhook 錯誤：{e}")
        abort(500)

    return 'OK'

# ✅ 處理使用者訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            parts = msg.split()
            reply = None

            # ✅ 查 K 線圖（預設30天）
            if len(parts) == 1 and parts[0].isdigit():
                path = crawler.generate_kline_image(parts[0])
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            # ✅ 查即時價格
            elif len(parts) == 2 and parts[1].lower() == 'now':
                info = crawler.get_realtime_price(parts[0])
                reply = TextMessage(text=info)

            # ✅ 區間查詢
            elif len(parts) == 3 and re.match(r'\d{4}-\d{2}-\d{2}', parts[1]) and re.match(r'\d{4}-\d{2}-\d{2}', parts[2]):
                path = crawler.generate_kline_image_by_date(parts[0], parts[1], parts[2])
                url = f"{crawler.IMAGE_HOST_URL}/{path}"
                reply = ImageMessage(original_content_url=url, preview_image_url=url)

            # ✅ 指令說明
            elif msg.lower() == '幫助':
                reply = TextMessage(text="📌 **指令說明：**\n"
                                         "🟥 `2330` → 查 K 線圖\n"
                                         "🟧 `2330 now` → 查即時價\n"
                                         "🟨 `2330 2024-01-01 2024-04-01` → 查區間圖\n"
                                         "🟩 `幫助` → 查看說明")

            else:
                reply = TextMessage(text="⚠️ 無法辨識的指令，請輸入『幫助』查看用法")

        except Exception as e:
            reply = TextMessage(text=f"❌ 發生錯誤：{e}")
            print(f"❌ 程式錯誤：{e}")

        # ✅ 發送回覆
        try:
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply]
            )
            line_bot_api.reply_message(req)
        except Exception as e:
            print(f"❌ 回覆 LINE 失敗：{e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
