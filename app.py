# 실행 방법 : flask --app app.py run --debug
from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True

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

