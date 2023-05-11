from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import PostbackAction,URIAction, MessageAction, TemplateSendMessage,CarouselTemplate,CarouselColumn
import os
import requests
import urllib.request
import json

app = Flask(__name__)
# LINE BOT info
line_bot_api = LineBotApi('wmKuQNPrXxJMR7xoE+p78dgywautUa6CjT3+GBOL2ntGTdADTD5nPApWZP8ApreDUQOhTffvJwT/ccPR9zsmESXpLa7xdxeKHRbdRoWgEwSfwNGqe7nVXSlvXjxM4p9+R5sSL9jgCqOnqpXwCjR4pQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('eca1c9014ad67b523ff5454a56029cb1')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
        #signature,LINE官方提供用來檢查該訊息是否透過LINE官方APP傳送
        #body,用戶傳送的訊息，並且是以JSON的格式傳送
    except InvalidSignatureError:
        abort(400)
    return 'OK'

cities = ['宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹縣', '新竹市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '屏東縣']

def get(city):
    token = 'CWB-CA507B14-5C33-419A-96E4-A4D6B22C2E95'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091?Authorization=' + token + '&format=JSON&locationName=' + str(city) + '&elementName=UVI'
    Data = requests.get(url)
    Data.encoding='utf-8'
    Data =Data.json()['records']['locations'][0]['location'][0]['weatherElement'][0]['time'] 
    return Data
# Message event
@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    if(event.message.text[:3] == '紫外線'):
        city = event.message.text[4:]
        city = city.replace('台','臺')
    # 使用者輸入的內容並非符合格式
        if(not (city in cities)):
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="查詢格式為:紫外線 縣市"))
        else:
            res = get(city)
            line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
                alt_text = city + '未來一周紫外線預測',
                template = CarouselTemplate(
                    columns = [
                        CarouselColumn(
                            thumbnail_image_url = 'https://burst.shopifycdn.com/photos/sun-setting-over-ocean.jpg?width=746&format=pjpg&exif=1&iptc=1',
                            title = city + '未來一周紫外線預測',
                            text = '{} ~ {}\n紫外線指數 {}\n曝曬級數 {}'.format(data['startTime'][5:-3],data['endTime'][5:-3],data['elementValue'][0]['value'],data['elementValue'][1]['value']),
                            actions = [
                                URIAction(
                                    label = '詳細內容',
                                    uri = 'https://www.cwb.gov.tw/V8/C/W/MFC_UVI_Map.html'
                                )
                            ]
                        )for data in res
                    ]
                )
            ))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
            #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
    #TextSendMessage,=要回覆的訊息


if __name__ == "__main__":
    app.run()