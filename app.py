from flask import Flask,jsonify
from dotenv import load_dotenv
import os
import requests
app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

# Access environment variables
VT_API_URL = os.getenv('VT_API_URL')
VT_SANDBOX_URL = os.getenv('VT_SANDBOX_URL')
API_KEY = os.getenv('API_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')

@app.route("/")
def hello_world():
    return {
        "status": True,
        "message": "You probably shouldn't be here, but...",
        "data": {
            "service": "wavepay-api",
            "version": "1.x"
        }
    }

@app.route('/api/vtpass-balance', methods=['GET'])
def get_vtpass_balance():
    headers = {
        'api-key': API_KEY,
        'public-key': PUBLIC_KEY
    }

    try:
        # Make GET request to the VTpass API
        response = requests.get(VT_SANDBOX_URL, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            balance_data = response.json()  
            return jsonify(balance_data) 
        else:
            return jsonify({
                "error": "Failed to retrieve balance",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)