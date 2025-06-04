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
sheet = client.open("Untitled form (Responses)").sheet1

# 2. Webhook endpoint (Google Apps Script trigger POSTs here)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    image_url = data.get('imageUrl')
    prompt = data.get('prompt', "Mongolian girl in fantasy style, beautiful lighting, high detail")
    last_row = len(sheet.get_all_values())
    # 3. DALL·E API - шинэ синтакс (openai-python >=1.0.0)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.images.generate(
        model="dall-e-3",  # "dall-e-2" гэж сольж болно
        prompt=prompt,
        n=1,
        size="1024x1024"
    )       
    output_url = response.data[0].url
        sheet.update_cell(last_row, 8, output_url)  # H багана
    except Exception as e:
        sheet.update_cell(last_row, 8, f"AI error: {str(e)}")
    return 'OK'
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
