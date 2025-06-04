import gspread
import requests
import openai
import os

openai.api_key = "YOUR_API_KEY"

gc = gspread.service_account(filename='client_secret.json')
ws = gc.open("SheetName").sheet1

def process_variation(row):
    image_url = ws.cell(row, 2).value  # B багана (Зурагны линк)
    
    # 1. Google Drive link direct download руу хөрвүүлж байна уу? (жишээ нь)
    if "drive.google.com" in image_url and "uc?export=download" not in image_url:
        # "id=" дараах хэсгийг олж, шинэ линк үүсгэнэ
        try:
            file_id = image_url.split("id=")[1]
            image_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        except Exception as e:
            print("Google Drive линк буруу байна:", e)
            return

    # 2. Зургийг татаж авах
    response = requests.get(image_url)
    if response.status_code != 200:
        print("Зураг татахад алдаа гарлаа:", response.status_code)
        return
    with open("temp.png", "wb") as f:
        f.write(response.content)

    # 3. DALL·E-2-р Variation хийх
    with open("temp.png", "rb") as img:
        dalle_resp = openai.Image.create_variation(
            image=img,
            n=1,
            size="1024x1024"
        )
    output_url = dalle_resp['data'][0]['url']

    # 4. H баганад зассан зурагны линк бичих
    ws.update_cell(row, 8, output_url)  # H = 8 дахь багана
    print("Зассан зурагны линк:", output_url)

    # 5. Түр файлыг устгах
    os.remove("temp.png")

# Жишээ нь 20-р мөрийг боловсруулах
process_variation(20)
