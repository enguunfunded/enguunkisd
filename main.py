from flask import Flask, request
import requests
import gspread  # Google Sheets
from oauth2client.service_account import ServiceAccountCredentials
import openai  # DALL·E API
import os

app = Flask(__name__)

# 1. Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("SheetName").sheet1

# 2. Webhook endpoint (Google Apps Script trigger POSTs here)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    image_url = data.get('imageUrl')
    # 3. DALL·E API - зураг янзлуулах
    openai.api_key = os.getenv("OPENAI_API_KEY")
    dalle_response = openai.Image.create(
        prompt="Mongolian girl in fantasy style, beautiful lighting, high detail",
        n=1,
        size="1024x1024",
        image=image_url
    )
    output_url = dalle_response['data'][0]['url']
    # 4. Google Drive upload эсвэл шууд Messenger рүү буцаах
    # 5. Messenger API рүү зургаа илгээх
    fb_url = "https://graph.facebook.com/v18.0/me/messages?access_token=PAGE_ACCESS_TOKEN"
    payload = {
        "recipient": {"id": data['messenger_id']},
        "message": {"attachment": {"type": "image", "payload": {"url": output_url}}}
    }
    requests.post(fb_url, json=payload)
    return 'OK'

if __name__ == '__main__':
    app.run(port=5000)
