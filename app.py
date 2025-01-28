from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

DEEPSEEK_API_URL = 'https://api.deepseek.com/your-endpoint'  # Replace with the actual DeepSeek API endpoint

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
        response = requests.post(DEEPSEEK_API_URL, json={'query': user_input})
        response_data = response.json()
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
