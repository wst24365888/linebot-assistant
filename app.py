from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, CarouselTemplate, CarouselColumn
)

import random as rd

import newton_separate

import urllib.request

import urllib.parse

import re

import os

import requests

from bs4 import BeautifulSoup

from user_agent import generate_user_agent

import json

import numpy as np

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

def dcard_top_5():

    reply = 'Dcard 熱門文章 Top 5\n'

    url = 'https://www.dcard.tw/f'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    dcard_titles = soup.find_all('h3', 'PostEntry_title_H5o4d PostEntry_unread_2U217')
    dcard_links = soup.find_all('a', 'PostEntry_root_V6g0r')

    dcard_article = []

    for i in range(5):
        dcard_article.append([dcard_titles[i].text, 'https://www.dcard.tw' + dcard_links[i]['href']])
    
    for index, item in enumerate(dcard_article):
        reply += '\n{}. {}\n{}\n'.format(index + 1, item[0], item[1])

    reply += '輸入\'q\'離開'
    
    return reply

def ptt_top_5():

    reply = 'PTT 熱門文章 TOP 5\n'

    url = 'https://disp.cc/m/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    ptt_titles = soup.find_all('div', 'ht_title')
    ptt_links = soup.find_all('a')

    ptt_article = []

    for i in range(5):
        ptt_article.append([ptt_titles[i].text, 'https://disp.cc/m/' + ptt_links[i]['href']])
    
    for index, item in enumerate(ptt_article):
        reply += '\n{}. {}\n{}\n'.format(index + 1, item[0], item[1])

    print('ok!!')

    reply += '輸入\'q\'離開'
    
    return reply

def newtalk_top_5():

    reply = 'NewTalk 即時新聞 TOP 5\n'

    url = 'http://newtalk.tw/news/summary/today'
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    newtalk_block_1 = soup.find_all('div', 'news-title')
    newtalk_block_2 = soup.find_all('div', 'text col-md-8 col-sm-8 col-xs-6')

    newtalk_article = []

    for i in range(2):
        newtalk_article.append([newtalk_block_1[i].text, newtalk_block_1[i].find('a')['href']])

    for i in range(3):
        newtalk_article.append([newtalk_block_2[i].find('div', 'news_title').text.strip(), newtalk_block_2[i].find('a')['href']])
    
    for index, item in enumerate(newtalk_article):
        reply += '\n{}. {}\n{}\n'.format(index + 1, item[0], item[1])

    reply += '輸入\'q\'離開'

    return reply

def train_timetable(messages):

    with open('20180618.json', 'r', encoding = 'utf-8-sig') as f1:
        data = json.loads(f1.read())

    station_dict = {}

    with open('stations.txt', 'r', encoding = 'utf-8-sig') as f2:
        for lines in f2:
            station_dict[lines.strip().split(':')[0]] = lines.strip().split(':')[1]

    dep_station = messages.split(',')[0]
    arr_station = messages.split(',')[1]

    reply = '從{}到{}的火車時刻表:\n'.format(dep_station, arr_station)

    dep_station = station_dict[dep_station]
    arr_station = station_dict[arr_station]

    timetable = []

    for i in range(len(data['TrainInfos'])):    

        train_profile = np.array([[d['Station'], d['ArrTime'], d['DepTime']] for d in data['TrainInfos'][i]['TimeInfos']])
        stations = train_profile[:,0]

        if dep_station in stations and arr_station in stations:

            dep_time = train_profile[list(stations).index(dep_station)][2]
            arr_time = train_profile[list(stations).index(arr_station)][1]

            dep_time_trans = int(dep_time.split(':')[0])*60 + int(dep_time.split(':')[1])

            hrs = int(arr_time.split(':')[0]) - int(dep_time.split(':')[0])
            mins = int(arr_time.split(':')[1]) - int(dep_time.split(':')[1])

            if hrs*60 + mins <= 0:
                continue
            else:
                timetable.append([data['TrainInfos'][i]['Train'], dep_time, arr_time, hrs*60 + mins, dep_time_trans])

    if timetable == []:

        reply += 'Sorry~\n發生了一些錯誤,可能原因:\n1. 此路徑沒有班次\n2. 格式錯誤'

    else:

        timetable = sorted(timetable, key = lambda element: element[4])

        for i in range(len(timetable)):
            reply += '車次: {}\t發車時間: {}\t 到達時間: {}\t搭車時間: {} 分鐘\n'.format(timetable[i][0], timetable[i][1], timetable[i][2], timetable[i][3])

    reply += '輸入\'q\'離開'
    
    return reply

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    template = TemplateSendMessage(
        alt_text='(選單)',
        template=CarouselTemplate(
            columns=[
            # Note:三個Carousel中actions都得要相同, 不然會整台掛掉
            CarouselColumn(
                thumbnail_image_url='https://truth.bahamut.com.tw/s01/201711/1264bad8430c679ef5c7ffd685244218.JPG',
                title='小工具',
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
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.ytimg.com/vi/A1LtAYGom9Y/maxresdefault.jpg',
                title='爬蟲',
                text='請選擇:',
                actions=[
                    MessageTemplateAction(
                        label='NewTalk 即時新聞 TOP 5',
                        text='NewTalk 即時新聞 TOP 5'
                    ),
                    MessageTemplateAction(
                        label='PTT 熱門文章 TOP 5',
                        text='PTT 熱門文章 TOP 5'
                    ),
                    MessageTemplateAction(
                        label='Dcard 熱門文章 TOP 5',
                        text='Dcard 熱門文章 TOP 5'
                    )
                ]
            ),
            CarouselColumn(
                thumbnail_image_url='https://i.pinimg.com/originals/53/07/1d/53071d73b869c9263b912e3b8a6fe459.gif',
                title='小工具 Part2',
                text='請選擇:',
                actions=[
                    MessageTemplateAction(
                        label='查詢火車時刻表',
                        text='查詢火車時刻表'
                    ),
                    MessageTemplateAction(
                        label='回到主頁',
                        text='回到主頁'
                    ),
                    MessageTemplateAction(
                        label='回到主頁',
                        text='回到主頁'
                    )
                ]
            )
            ]
        )
    )

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

    if ('早' in cmd or '嘿' in cmd or '安' in cmd or '嗨' in cmd or  '你好' in cmd or'hello' in cmd or 'hi' in cmd or 'hey' in cmd) and mode != 3:

        mode = 0

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))

        print('打招呼')

        reply = hello()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "{}".format(reply)))

        return 0

    elif '回到主頁' in cmd or '功能' in cmd or '選單' in cmd:

        mode = 0

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))

        print(mode)

        line_bot_api.reply_message(
            event.reply_token,
            template
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

    elif ('查詢火車時刻表' in cmd) and mode != 3:

        mode = 4

        with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
            f.write(str(mode))

        print('mode')
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
            alt_text='(選單)',
            template=ButtonsTemplate(
                title='查詢火車時刻表',
                text='請輸入\'起站,迄站\'\nex. 永康,保安',
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

    elif 'NewTalk 即時新聞 TOP 5' in cmd:

        reply = newtalk_top_5()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "{}".format(reply)))

        return 0  

    elif 'PTT 熱門文章 TOP 5' in cmd:

        print('ok!')

        reply = ptt_top_5()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "{}".format(reply)))

        return 0    

    elif 'Dcard 熱門文章 TOP 5' in cmd:

        reply = dcard_top_5()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "{}".format(reply)))

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

        elif mode == 4:

            reply = train_timetable(cmd)
        
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text = "{}".format(reply)))

            return 0

        else:

            mode = 0

            with open('{}_cmd.txt'.format(profile.user_id), 'w') as f:
                f.write(str(mode))
            
            print(mode)

            line_bot_api.reply_message(
                event.reply_token,
                template
            )

            return 0

if __name__ == "__main__":
    app.run()