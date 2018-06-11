from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import random as rd

app = Flask(__name__)

line_bot_api = LineBotApi('ew9Gu+/a0OB/IT90r8mEiLaipylgz85Kw9maa8624PWPZsvnggQrt1iEbkMaPXFyJD+u6P3zmvMYiY3k3fu0+/c6lGZTcpG0AdeUs+ChuJ00knWPevFv2Jxnjnv6b+J9BmZkBGO5Zsms74pn42KasAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c90f608354cca2df82c4e2b6167097c9')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    message = event.message.text
    reply = '目前有以下功能哦~\n1. 抽數字\nusage:\t抽,min,max'

    if '早' in message or '安' in message or '嗨' in message or 'hello' in message or 'hi' in message:
        reply = '安安'
    elif '抽' in message:
        trash, min_num, max_num = message.split(',')
        min_num = int(min_num)
        max_num = int(max_num)
        reply = '{}'.format(rd.randint(min_num,max_num))

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = reply))



if __name__ == "__main__":
    app.run()