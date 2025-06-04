from flask import Flask, request
import requests
import os
import gspread
import time
from threading import Thread

# ------------------ ТОХИРГОО ------------------
PAGE_ACCESS_TOKEN = 'YOUR_PAGE_ACCESS_TOKEN'
VERIFY_TOKEN = 'YOUR_VERIFY_TOKEN'
GOOGLE_SHEET_NAME = 'Untitled form (Responses)'
GOOGLE_CREDENTIALS = '/etc/secrets/service_account.json'
# ----------------------------------------------

# Google Sheets тохиргоо
gc = gspread.service_account(filename=GOOGLE_CREDENTIALS)
sh = gc.open(GOOGLE_SHEET_NAME)
ws = sh.sheet1

app = Flask(__name__)

# Webhook энд ажиллана
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification token mismatch', 403
    elif request.method == 'POST':
        data = request.json
        for entry in data['entry']:
            for msg in entry['messaging']:
                if 'message' in msg:
                    handle_message(msg)
        return "ok", 200

def handle_message(msg):
    sender = msg['sender']['id']
    message = msg['message']
    # Зураг илгэсэн эсэхийг шалгана
    if 'attachments' in message:
        for att in message['attachments']:
            if att['type'] == 'image':
                image_url = att['payload']['url']
                save_order(sender, image_url, '')  # Сонголтыг дараа нь авах
                quick_reply(sender)
    elif 'quick_reply' in message:
        payload = message['quick_reply']['payload']
        update_service(sender, payload)
        send_payment_instruction(sender)
    elif 'text' in message and 'баримт' in message['text']:
        update_payment(sender)
        send_text(sender, "Төлбөр баталгаажлаа! Таны зураг удахгүй засагдаж илгээгдэнэ.")
    else:
        send_text(sender, "Зураг илгээнэ үү.")

def quick_reply(sender):
    data = {
        "recipient": {"id": sender},
        "message": {
            "text": "Ямар засвар хийх вэ?",
            "quick_replies": [
                {"content_type": "text", "title": "Фон солих", "payload": "BG_CHANGE"},
                {"content_type": "text", "title": "Гэрэл засах", "payload": "LIGHT_EDIT"},
                {"content_type": "text", "title": "Зургаа өөрчлөх", "payload": "EDIT_IMG"}
            ]
        }
    }
    requests.post(f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}", json=data)

def save_order(sender, image_url, service):
    ws.append_row([sender, image_url, service, 'pending', '', ''])  # Messenger ID, image, service, status, paid, done_img

def update_service(sender, service):
    cell = ws.find(sender)
    ws.update_cell(cell.row, 3, service)

def send_payment_instruction(sender):
    text = "Төлбөрийн QR/линк: [энд оруулна]\nТөлбөр хийсний дараа 'баримт' гэж бичээрэй."
    send_text(sender, text)

def update_payment(sender):
    cell = ws.find(sender)
    ws.update_cell(cell.row, 5, 'paid')

def send_text(sender, text):
    data = {
        "recipient": {"id": sender},
        "message": {"text": text}
    }
    requests.post(f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}", json=data)

def send_image(sender, image_url):
    data = {
        "recipient": {"id": sender},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url}
            }
        }
    }
    requests.post(f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}", json=data)

# Админ Sheet-ийг polling хийж, шинэ зураг илгээнэ
def poll_and_reply():
    while True:
        records = ws.get_all_records()
        for idx, rec in enumerate(records, start=2):
            if rec['done_img'] and rec['status'] != 'sent':
                send_image(rec['messenger_id'], rec['done_img'])
                ws.update_cell(idx, 4, 'sent')  # Статусыг шинэчилнэ
        time.sleep(60)

if __name__ == '__main__':
    # Sheet polling loop-г тусдаа thread дээр ажиллуулна
    Thread(target=poll_and_reply, daemon=True).start()
    app.run(port=5000)
