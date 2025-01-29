from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

DEEPSEEK_API_URL = 'https://api.deepseek.com'  # Replace with the actual DeepSeek API endpoint

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    # Proxy the request to DeepSeek API
    try:
        oaiclient = OpenAI()
        oaiclient.api_key = os.getenv("OPENAI_API_KEY")
        response = oaiclient.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": user_input},
            ],
            stream=False
        )
        response_data = response.choices[0].message.content
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
