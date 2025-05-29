import stock_crawler as crawler
import os
import re
msg_parts = "2330 2025-04-01 2025-04-30".split(r" ")
if len(msg_parts) == 3 and re.match(r'^\d{4}-\d{2}-\d{2}$', msg_parts[1]) and re.match(r'^\d{4}-\d{2}-\d{2}$', msg_parts[2]):
        stock_id, start_date, end_date = msg_parts
        path = crawler.generate_kline_image_by_date(stock_id, start_date, end_date)
        image_url = f"{crawler.IMAGE_HOST_URL}/{path}"
        
        print(image_url)
