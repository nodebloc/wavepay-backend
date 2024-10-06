from flask import Flask,jsonify
from dotenv import load_dotenv
import os
import requests
app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

# Access environment variables
VT_API_URL = os.getenv('VT_API_URL')

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

# function for connect to Vt Pass Telecom

def connectToApi(vtPassEndpoint, errorMessage,exceptionErrorMessage):
    headers = {'api-key': API_KEY,'public-key': PUBLIC_KEY}
    try:
        # Make GET request to the VTpass API
        response = requests.get(vtPassEndpoint, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()  
            return jsonify(data) 
        else:
            return jsonify({
                "error": errorMessage,
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"status": False, "message": exceptionErrorMessage, "error": str(e)}), 500

@app.route('/api/vtpass-balance', methods=['GET'])
def get_vtpass_balance():
    VT_SANDBOX_URL = os.getenv('VT_SANDBOX_URL_BALANCE')
    result = connectToApi(VT_SANDBOX_URL, "Failed to retrived Balance", "An error Occur")
    return result

@app.route('/api/vtpass-categories', methods=['GET'])
def get_vtpass_categories():
    VT_SANDBOX_URL = os.getenv('VT_SANDBOX_URL_CATEGORIES')
    result = connectToApi(VT_SANDBOX_URL, "Failed to retrived Categories", "An error Occur")
    return result

if __name__ == "__main__":
    app.run(debug=True)