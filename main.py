from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def home():
    return "Сервер ажиллаж байна!"

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    prompt = f"{data['parent_name']} {data['style']} зураг: {data['image_link']}"
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1)
        image_url = response.data[0].url
        return jsonify({"status": "success", "image_url": image_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
