import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
API_URL = "https://api.replicate.com/v1/predictions"
VERSION = "7762f7d0f7f82c948538e41f63f77d6850e02b063e37e496e0eefd46c929f9bd"  # Жишээ SDXL version

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get("image_link")
    style = data.get("style", "")
    extra = data.get("extra", "")
    prompt = f"{style} {extra}".strip()

    # Зөв 4 space ашиглаж эхлүүл!
  replicate_payload = {
    "version": "7762f7d0f7f82c948538e41f63f77d6850e02b063e37e496e0eefd46c929f9bd",
    "input": {
        "image": image_url,
        "prompt": prompt,
    }
}

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.post(API_URL, json=replicate_payload, headers=headers)
    try:
        prediction = r.json()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    try:
        output_url = prediction.get("output")[0]
        return jsonify({"status": "success", "image_url": output_url})
    except Exception as e:
        return jsonify({"status": "error", "message": prediction.get("error", str(e))})

if __name__ == '__main__':
    app.run(debug=True)
