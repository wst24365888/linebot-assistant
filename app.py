from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate
)

import random as rd

import newton_separate

import urllib.request

import urllib.parse

import re

from user_agent import generate_user_agent

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

    if ' ' in event.message.text:
        cmd, messages = event.message.text.split()
    else:
        cmd = event.message.text

    reply = '目前有以下功能哦~\n\n1. 抽數字\n輸入\'抽 min,max\'\nex.\ninput: 抽 1,100\noutput: 87\n\n2. 多項式拆出一次式\n輸入\'拆 terms1,terms2,...\'\nex.\ninput: 拆 1,2,1\noutput: (x+1)\n\n3. 找圖片\nex.\ninput: 找 紅米,Note4X;n\noutput: Google搜圖的第n個結果\nNote. 可以多關鍵字, 輸入時請用逗號分開; n可以不輸入, 預設為1'

    if '早' in cmd or '嘿' in cmd or '安' in cmd or '嗨' in cmd or  '你好' in cmd or'hello' in cmd or 'hi' in cmd or 'hey' in cmd:
        hello_seed = rd.randint(1,4)
        if hello_seed == 1:
            reply = '安安'
        elif hello_seed == 2:
            reply = '嗨'
        elif hello_seed == 3:
            reply = 'hi'
        elif hello_seed == 4:
            reply = 'hello'

    elif '抽' in cmd:

        min_num, max_num = messages.split(',')
        min_num = int(min_num)
        max_num = int(max_num)
        reply = '{}'.format(rd.randint(min_num,max_num))

    elif '拆' in cmd:

        reply = newton_separate.run_main(messages)

    elif '找' in cmd:

        n = 0

        check = 0

        if ';' in messages:
            messages, n = messages.split(';')
            n = int(n)-1

        keyword = ''

        if ',' not in messages:
            keyword = urllib.parse.quote_plus('{}'.format(messages))
        else:
            for i in range(len(messages.split(','))):
                keyword += urllib.parse.quote_plus('{}'.format(messages.split(',')[i]))
                if i == len(messages.split(','))-1:
                    break
                else:
                    keyword += '+'                    

        url = 'https://www.google.com/search?source=lnms&tbm=isch&q={}'.format(keyword)

        headers = {}
        headers['User-Agent'] = generate_user_agent()
        headers['Referer'] = 'https://www.google.com'
        req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req)
        data = str(resp.read())

        try:
            img_url = re.findall('"ou":"(.*?)"', data)[int(n)-1]
            test_url = urllib.request.urlopen(img_url)
        except IndexError:
            check = 1
        except urllib.error.HTTPError as error:
            print('{}'.format(error))
            check = 1

        if 'https' not in img_url or check == 1:
            reply = 'Sorry~\n發生了一些錯誤,可能原因:\n1. 找不到,換個關鍵字吧!\n2. 網站掛了QQ\n3. 圖片網址不安全\n4. 格式錯誤'
        else:
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=img_url,
                    preview_image_url=img_url))

    elif 'test' in cmd:

        #profile = line_bot_api.get_profile(event.source.user_id)
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                thumbnail_image_url='https://example.com/image.jpg',
                title='Menu',
                text='Please select',
                actions=[
                    MessageAction(
                        label='message1',
                        text='1'
                    ),
                    MessageAction(
                        label='message2',
                        text='2'
                    ),
                    MessageAction(
                        label='message3',
                        text='3'
                    )
                ]
            )
            )
        )
        
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = "{}".format(reply)))


if __name__ == "__main__":
    app.run()