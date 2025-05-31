import requests
from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

# Replicate API Key -г Environment variable-ээс авч байна.
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

@app.route('/')
def home():
    return "Сервер ажиллаж байна!"

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get('image_link', '')
    style = data.get('style', '')
    extra = data.get('extra', '')
    prompt = f"{style}, {extra}"

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    version = "fdfe5a21a2369e9c3a9c13d3a97c205e224f2d63a02cf2a6b86e904265be10df"  # SDXL img2img
    api_url = "https://api.replicate.com/v1/predictions"

    input_data = {
        "version": version,
        "input": {
            "image": image_url,
            "prompt": prompt,
            "strength": 0.7
        }
    }

    # Replicate API руу хүсэлт илгээж, статусыг poll хийж, output-г нь буцаана
    try:
        response = requests.post(api_url, headers=headers, json=input_data)
        prediction = response.json()
        prediction_url = prediction["urls"]["get"]

        for _ in range(60):
            poll = requests.get(prediction_url, headers=headers)
            poll_data = poll.json()
            if poll_data["status"] == "succeeded":
                return jsonify({"status": "success", "image_url": poll_data["output"][0]})
            elif poll_data["status"] == "failed":
                return jsonify({"status": "error", "message": poll_data.get("error", "Unknown error")})
            time.sleep(2)
        return jsonify({"status": "error", "message": "Timed out waiting for Replicate"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
