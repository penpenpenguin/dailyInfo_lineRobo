from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from bs4 import BeautifulSoup
import requests
import os

line_bot_api = LineBotApi('ptgLxCu1ytg/M362kQvXn7MQjtjZsa+I9Rf/uJ2tY4WDsAxpKa6+pLQB9nfwbYuePinUiLKyVXs2gyF7bPJndutB1qkH038j878ydjvmmMpp+24Pik1gaH+eoJwEWAQgqRJkeFAR8/mWyCxhbWzhLAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9a4ff0cfbb03ac509ba95b0836ecad37')

app = Flask(__name__)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    message = event.message.text
    if message[0] == '星' and message[1] == '座' and message[2] == ' ':
        star = message.split('星座 ')[1]
        constellationResult = getConstellation(star)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=constellationResult))


  
@app.route('/star/<string:star>', methods=['GET'])
def getConstellation(star):
    resultString = constellation(star)
    return resultString

def constellation(star):
    constellationDict = {'牡羊': 'aries', '金牛': 'taurus', '雙子': 'gemini','巨蟹': 'cancer',
                            '獅子': 'leo', '處女': 'virgo', '天秤': 'libra','天蠍': 'scorpio', 
                            '射手': 'sagittarius', '摩羯':'capricorn','水瓶': 'aquarius', '雙魚': 'pisces'}
    resultString = ''
    resultString += '***************************今日運勢***************************\n'

    urlOrz= 'https://horoscope.dice4rich.com/?sign={}'.format(constellationDict[star])
    res = requests.get(urlOrz)
    # 指定 html.parser 作為解析器
    soup = BeautifulSoup(res.text,'html.parser')

    title = soup.select('.current .title')
    content = soup.select('.current .content')

    for i in range(len(title)+len(content)):
        if i%2 == 0:
            print(title[int(i/2)].text.strip())
            resultString += title[int(i/2)].text.strip() + '\n'
        else:
            print(content[int(i/2)].text)
            resultString += content[int(i/2)].text + '\n\n'
    
    resultString += '-以下內容來自小歐星座網站-' + '\n'
    return resultString           
                 
if __name__ == "__main__":
    app.run()