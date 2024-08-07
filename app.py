# 실행 방법 : flask --app app.py run --debug
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True

@app.route('/urls', methods=['POST'])
def urls():
    data = request.json
    url = data.get('url', '')

    app.logger.info(f"Received URL: {url}")
    
    if not url:
        app.logger.error("No URL provided")
        return jsonify({'status': 'error', 'message': 'URL을 제공해 주세요.'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        app.logger.info(f"URL fetch successful: {url}")
    
    except requests.RequestException as e:
        app.logger.error(f"Error fetching URL: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    try: 
        result = subprocess.run(
            ['python', 'Ceawling/web-crawling.py', url],
            capture_output=True,
            text=True,
            check=True
        )
        app.logger.info(f"Script output: {result.stdout}")
        return jsonify({'status': 'success', 'output': result.stdout})
    
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error running script: {e.stderr}")
        return jsonify({'status': 'error', 'output': e.stderr}), 500


@app.route('/reviews', methods=['POST'])
def reviews():
    file_path = 'navershopping_review.json'
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found!"}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    
        if not isinstance(data, list):
            return jsonify({"error": "JSON data is not in the expected format!"}), 500

        rd_ranks = [item.get("RD_RANK") for item in data if "RD_RANK" in item]
        
        if not rd_ranks:
            app.logger.error("No RD_RANK key found in any of the JSON objects.")
            return jsonify({"error": "No RD_RANK key found in JSON data!"}), 404
        
    except json.JSONDecodeError as e:
        return jsonify({"error": "Error decoding JSON file!"}), 500
    
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred!"}), 500

    return jsonify({"RD_RANK" : rd_ranks})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

