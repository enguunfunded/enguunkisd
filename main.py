import gspread
import requests
import openai
import os

openai.api_key = "YOUR_API_KEY"

gc = gspread.service_account(filename='client_secret.json')
ws = gc.open("SheetName").sheet1

def process_variation(row):
    image_drive_link = ws.cell(row, 2).value  # B багана
    # 1. Drive линкээс file ID авах
    import re
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', image_drive_link)
    if not match:
        print("Drive линк буруу байна!")
        return
    file_id = match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(download_url)
    if response.status_code != 200:
        print("Зураг татаж чадсангүй.")
        return

    with open("temp.png", "wb") as f:
        f.write(response.content)

    # PNG, 1024x1024 эсэхийг шалгахыг зөвлөе!

    with open("temp.png", "rb") as img:
        dalle_resp = openai.Image.create_variation(
            image=img,
            n=1,
            size="1024x1024"
        )
    output_url = dalle_resp['data'][0]['url']
    ws.update_cell(row, 8, output_url)
    print("Зассан зурагны линк:", output_url)


    # 5. Түр файлыг устгах
    os.remove("temp.png")

# Жишээ нь 20-р мөрийг боловсруулах
process_variation(20)
