import gspread
import requests
import openai

openai.api_key = "YOUR_API_KEY"

gc = gspread.service_account(filename='client_secret.json')
ws = gc.open("SheetName").sheet1

def process_variation(row):
    image_url = ws.cell(row, 2).value  # B багана
    response = requests.get(image_url)
    with open("temp.png", "wb") as f:
        f.write(response.content)

    with open("temp.png", "rb") as img:
        dalle_resp = openai.Image.create_variation(
            image=img,
            n=1,
            size="1024x1024"
        )
    output_url = dalle_resp['data'][0]['url']
    ws.update_cell(row, 8, output_url)  # H багана
    print("Зассан зурагны линк:", output_url)

# Жишээ нь 20-р мөрийг боловсруулах
process_variation(20)
