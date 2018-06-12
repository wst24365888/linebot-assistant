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

import newton_separate

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
    reply = '目前有以下功能哦~\n\n1. 抽數字\n輸入\'抽\'呼叫\n\n2. 多項式拆出一次式\n輸入\'拆\''

    if '早' in message or '安' in message or '嗨' in message or  '你好' in message or'hello' in message or 'hi' in message:
        mode = 0
        reply = '安安'
    elif '抽' in message:
        mode = 1
        reply = '輸入 min,max 即會從範圍裡抽一個數字\nex.\ninput: 1,100\noutput: 87'
    elif '拆' in message:
        mode = 2
        reply = '輸入多項式的各項係數並用逗號分開\nex.\ninput: 1,2,1\noutput: (x+1)'
    else:
        mode = 0


    if mode == 1:
        min_num, max_num = message.split(',')
        min_num = int(min_num)
        max_num = int(max_num)
        reply = '{}'.format(rd.randint(min_num,max_num))
        mode = 0
    elif mode == 2:
        reply = run_main(message.split(','))
        mode = 0

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = reply))



if __name__ == "__main__":
    app.run()