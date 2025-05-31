import requests
from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

@app.route('/')
def home():
    return "Replicate сервер ажиллаж байна!"

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get('image_link')
    style = data.get('style')
    extra = data.get('extra', '')

    prompt = f"{style}. {extra}"

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    # Та өөрийн сонгосон загварын version-ийг энд тавина
    version = "r8_JaxkfXYEHSTS5bhokSi5O7FjeVGqVOy4EMJXkc"  # sdxl model (2024 оны шинэ хувилбар)
    api_url = "https://api.replicate.com/v1/predictions"
    input_data = {
        "version": version,
        "input": {
            "image": image_url,        # хэрэглэгчийн оруулсан зураг
            "prompt": prompt,          # стиль + нэмэлт
            "strength": 0.7            # (0.5-1, ихэсгэх тусам илүү их өөрчилнө)
        }
    }
    response = requests.post(api_url, headers=headers, json=input_data)
    prediction = response.json()

    # Replicate нь async тул статусыг нь шалгаж, гүйцэтэл нь poll хийдэг.
    prediction_url = prediction['urls']['get']

    for _ in range(60):  # 60 сек дотор дуусна
        poll = requests.get(prediction_url, headers=headers)
        poll_data = poll.json()
        status = poll_data['status']
        if status == "succeeded":
            output_url = poll_data['output'][0]
            return jsonify({"status": "success", "image_url": output_url})
        elif status == "failed":
            return jsonify({"status": "error", "message": poll_data.get('error', 'Unknown error')})
        time.sleep(2)

    return jsonify({"status": "error", "message": "Timed out waiting for Replicate"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
