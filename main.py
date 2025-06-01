import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
API_URL = "https://api.replicate.com/v1/predictions"
VERSION = "7762f7d0f7f82c948538e41f63f77d6850e02b063e37e496e0eefd46c929f9bd"  # SDXL img2img (2024/06)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get("image_link")
    style = data.get("style", "")
    extra = data.get("extra", "")
    prompt = f"{style} {extra}".strip()

    # Replicate payload
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

    try:
        r = requests.post(API_URL, json=replicate_payload, headers=headers)
        prediction = r.json()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Replicate API call error: {str(e)}"
        })

    # --- Амжилттай эсэхийг шалгах, дэлгэрэнгүй логтой ---
    try:
        output = prediction.get("output")
        # Амжилттай бол зурган линк авах
        if output and isinstance(output, list) and len(output) > 0:
            output_url = output[0]
            return jsonify({"status": "success", "image_url": output_url})
        else:
            # Амжилтгүй бол log-г дэлгэрэнгүй харуулна
            return jsonify({
                "status": "error",
                "message": f"Replicate-ээс зураг буцаасангүй! details: {prediction}"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}, API response: {prediction}"
        })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
