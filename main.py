import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
API_URL = "https://api.replicate.com/v1/predictions"
VERSION = "b39d44c8db6d7cb0a5e69f7d1a16c26d6cd60fa6a248d095a6073d681c9ba02c"  # SDXL

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get("image_link")
    style = data.get("style", "")
    extra = data.get("extra", "")
    prompt = f"{style} {extra}".strip()

    # Replicate payload (ЗӨВХӨН "image" field, "urls" биш!)
    replicate_payload = {
        "version": VERSION,
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

    # Replicate-ийн output structure-г шалгаарай!
    try:
        output_url = prediction.get("output")[0]  # Зурагны линк ихэнхдээ ингэж ирдэг
        return jsonify({"status": "success", "image_url": output_url})
    except Exception as e:
        return jsonify({"status": "error", "message": prediction.get("error", str(e))})

if __name__ == '__main__':
    app.run(debug=True)
