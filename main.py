from flask import Flask, request
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import os

app = Flask(__name__)

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Untitled form (Responses)").sheet1

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    image_url = data.get('imageUrl')
    prompt = data.get('prompt', "Mongolian girl in fantasy style, beautiful lighting, high detail")
    last_row = len(sheet.get_all_values())
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        output_url = response.data[0].url
        sheet.update_cell(last_row, 8, output_url)  # H багана
    except Exception as e:
        sheet.update_cell(last_row, 8, f"AI error: {str(e)}")
    return 'OK'

if __name__ == '__main__':
    app.run(port=5000)
