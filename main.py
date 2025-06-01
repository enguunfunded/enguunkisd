import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
API_URL = "https://api.replicate.com/v1/predictions"
VERSION = "7762f7d0f7f82c948538e41f63f77d6850e02b063e37e496e0eefd46c929f9bd"  # SDXL (2024.06)
# ... бусад код нь хэвээр ...
@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    image_url = data.get("image_link")
    style = data.get("style", "")
    extra = data.get("extra", "")
    prompt = f"{style} {extra}".strip()

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

    try:
        r = requests.post(API_URL, json=replicate_payload, headers=headers)
        prediction = r.json()
        print("REPLICATE RESPONSE:", prediction)  # Хариуг log болго

        # Error ирсэн бол шууд харуул
        if prediction.get("error"):
            return jsonify({"status": "error", "message": prediction["error"]})

        # Output array ирсэн эсэхийг шалгах
        output = prediction.get("output")
        if output and isinstance(output, list) and len(output) > 0:
            return jsonify({"status": "success", "image_url": output[0]})
        else:
            return jsonify({
                "status": "error",
                "message": "Replicate-с зураг буцаасангүй: " + str(prediction)
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
