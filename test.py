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
#msg_parts = "2330 2024-01-01 2024-04-01".split(r" ")
'''
msg_parts = "2330 2024-04-01 2024-04-05".split(r" ")
if len(msg_parts) == 3 and re.match(r'^\d{4}-\d{2}-\d{2}$', msg_parts[1]) and re.match(r'^\d{4}-\d{2}-\d{2}$', msg_parts[2]):
        stock_id, start_date, end_date = msg_parts
        path = crawler.generate_kline_image_by_date(stock_id, start_date, end_date)
        image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
        
        print(image_url)
'''


#sma defualt is false
path = crawler.generate_kline_image(2330, 5, show_sma=False)
image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
reply = ImageMessage(original_content_url=image_url, preview_image_url=image_url)