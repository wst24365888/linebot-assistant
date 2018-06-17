from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction
)

import random as rd

import newton_separate

import urllib.request

import urllib.parse

import re

import os

from user_agent import generate_user_agent

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['line_bot_api'])
handler = WebhookHandler(os.environ['handler'])


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

def hello():

    hello_seed = rd.randint(1,4)
    if hello_seed == 1:
        reply = '安安'
    elif hello_seed == 2:
        reply = '嗨'
    elif hello_seed == 3:
        reply = 'hi'
    elif hello_seed == 4:
        reply = 'hello'

    return reply

def choose_num(messages):

    min_num, max_num = messages.split(',')
    min_num = int(min_num)
    max_num = int(max_num)
    reply = '{}'.format(rd.randint(min_num,max_num))

    return reply

def find_img(messages):    

    n = 0

    check = 0

    img_url = ''

    keyword = ''

    if ',' in messages:
        messages, n = messages.split(',')
        n = int(n)-1

    if ' ' not in messages:
        keyword = urllib.parse.quote_plus('{}'.format(messages))
    else:
        for i in range(len(messages.split())):
            keyword += urllib.parse.quote_plus('{}'.format(messages.split()[i]))
            if i == len(messages.split())-1:
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

    return img_url, check

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    profile = line_bot_api.get_profile(event.source.user_id)

    cmd = event.message.text

    try:
        with open('{}_cmd.txt'.format(profile.user_id), 'r') as f:
            for lines in f:
                mode = int(lines)
    except:
        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            mode = 0
            f.write(str(mode))

    print(cmd)

    if '早' in cmd or '嘿' in cmd or '安' in cmd or '嗨' in cmd or  '你好' in cmd or'hello' in cmd or 'hi' in cmd or 'hey' in cmd:

        mode = 0

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))

        print('打招呼')

        reply = hello()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "{}".format(reply)))

        return 0

    elif '回到主頁' in cmd or '功能' in cmd:

        mode = 0

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))

        print(mode)

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='(選單)',
            template=ButtonsTemplate(
                thumbnail_image_url='https://i.pinimg.com/originals/53/07/1d/53071d73b869c9263b912e3b8a6fe459.gif',
                title='現有功能',
                text='請選擇:',
                actions=[
                    MessageTemplateAction(
                        label='抽數字',
                        text='抽數字'
                    ),
                    MessageTemplateAction(
                        label='拆解多項式',
                        text='拆解多項式'
                    ),
                    MessageTemplateAction(
                        label='找圖片',
                        text='找圖片'
                    )
                ]
            )
            )
        )

        return 0

    elif '抽數字' in cmd:

        mode = 1

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))
            
        print(mode)
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='(選單)',
            template=ButtonsTemplate(
                title='抽數字',
                text='請輸入\'min,max\'\nex. 1,100',
                actions=[
                    MessageTemplateAction(
                        label='回到主頁',
                        text='回到主頁'
                    )
                ]
            )
            )
        )

        return 0

    elif '拆解多項式' in cmd:

        mode = 2

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))
            
        print(mode)
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='(選單)',
            template=ButtonsTemplate(
                title='拆解多項式',
                text='請輸入\'terms1,terms2,...\'\nex. 1,-2,1',
                actions=[
                    MessageTemplateAction(
                        label='回到主頁',
                        text='回到主頁'
                    )
                ]
            )
            )
        )

        return 0

    elif '找圖片' in cmd:

        mode = 3

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))
            
        print(mode)
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='(選單)',
            template=ButtonsTemplate(
                title='找圖片',
                text='請輸入\'關鍵字,指定筆數(預設為1)\'\nex. 紅米 Note4X,2',
                actions=[
                    MessageTemplateAction(
                        label='回到主頁',
                        text='回到主頁'
                    )
                ]
            )
            )
        )

        return 0
                    
    else:

        if mode == 1:

            reply = choose_num(cmd)
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "{}".format(reply)))

            return 0

        elif mode == 2:

            reply = newton_separate.run_main(cmd)
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "{}".format(reply)))

            return 0

        elif mode == 3:

            img_url, check = find_img(cmd)

            print('{},{}'.format(img_url, check))

            if 'https' not in img_url or check == 1:

                reply = 'Sorry~\n發生了一些錯誤,可能原因:\n1. 找不到,換個關鍵字吧!\n2. 網站掛了QQ\n3. 圖片網址不安全\n4. 格式錯誤'
        
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = "{}".format(reply)))

                return 0

            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url=img_url,
                        preview_image_url=img_url))

            return 0

        else:

            mode = 0

            with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
                f.write(str(mode))
            
            print(mode)

            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                alt_text='(選單)',
                template=ButtonsTemplate(
                    thumbnail_image_url='https://i.pinimg.com/originals/53/07/1d/53071d73b869c9263b912e3b8a6fe459.gif',
                    title='現有功能',
                    text='請選擇:',
                    actions=[
                        MessageTemplateAction(
                            label='抽數字',
                            text='抽數字'
                        ),
                        MessageTemplateAction(
                            label='拆解多項式',
                            text='拆解多項式'
                        ),
                        MessageTemplateAction(
                            label='找圖片',
                            text='找圖片'
                        )
                    ]
                )
                )
            )

            return 0

if __name__ == "__main__":
    app.run()