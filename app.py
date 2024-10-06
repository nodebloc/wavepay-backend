from flask import Flask,jsonify,request
from dotenv import load_dotenv
import os
import requests
import random
import string
from datetime import datetime
import pytz
app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

# Access environment variables
VT_API_URL = os.getenv('VT_API_URL')

API_KEY = os.getenv('API_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
SECRET_KEY =os.getenv('SECRET_KEY')
headers = {'api-key': API_KEY,'public-key': PUBLIC_KEY}

serviceId ={
        "mtn":"mtn-data",
        "airtel": "airtel-data",
        "glo": "glo-data",
        "glo-sme": "glo-sme-data",
        "etisalat":"etisalat-data",
        "etisalat-sme": "9mobile-sme-data"

    }

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

# Function to generate a request ID
def generate_request_id():
    # Set timezone to Africa/Lagos (GMT+1)
    lagos_timezone = pytz.timezone('Africa/Lagos')

    # Get current date and time in Lagos timezone
    current_time = datetime.now(lagos_timezone)

    # Format the date and time as YYYYMMDDHHMM (year, month, day, hour, minute)
    formatted_time = current_time.strftime('%Y%m%d%H%M')

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    request_id = formatted_time + random_string

    return request_id
# function that does the actual purchasing
def purchase_product(phone_number, amount, service_id):
    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'request_id':generate_request_id(),
        'serviceID': service_id,
        'amount': amount,
        'phone': phone_number
        
    }

    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_PURCHASE')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Could not make purchase",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500


# Buying products
@app.route('/api/vtpass-purchase', methods=['POST'])
def purchase():
    data = request.json  
    phone_number = data.get('phone')  
    amount = data.get('amount')
    service_id = data.get('serviceId')

    if not phone_number or not amount or not service_id: 
        return jsonify({"error": "Phone number and amount are required"}), 400

    # Call the purchase_product function to interact with VTpass API
    result = purchase_product(phone_number, amount, service_id)

    if result:
        return result

# Transaction status for anytime purchase
@app.route('/transaction-status', methods=['POST'])
def check_transaction_status():
    header = {'api-key': API_KEY,'public-key': PUBLIC_KEY,'secret-key': SECRET_KEY}
    try:
        
        
        # VTpass transaction status endpoint
        url = "https://sandbox.vtpass.com/api/requery"
        
        # Payload with the request_id
        # try and set this dynamically
        payload = {
            "request_id": "202410060616xkK5eoSbHc"
        }
        
        # Send POST request to VTpass with basic auth
        response = requests.post(url, json=payload, headers = header)
        
        # Get the JSON response
        data = response.json()
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
# Data subcription
@app.route('/get-variation-code', methods=['GET'])
def get_variation_codes():
    
    network= request.json  
    network = network.get('network')  
    url = os.getenv("VT_SANDBOX_URL_VARIATION_CODE")
    url="{}{}".format(url,serviceId[network])
    response = requests.get(url, headers = headers)
    data = response.json()
    
    return jsonify(data)

# Making payment 

# function that does the actual purchasing
def purchase_data(phone_number ,service_id_code, variation_code):
    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'request_id':generate_request_id(),
        'serviceID': serviceId[service_id_code],
        'phone':phone_number,
        # 'amount': amount,
        'billersCode': phone_number,
        'variation_code': variation_code
        
    }

    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_PURCHASE_DATA')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Could not make purchase",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500


# Buying data
@app.route('/api/vtpass-purchase-data', methods=['POST'])
def purchase_data_subcription():
    data = request.json  
    phone_number = data.get('phone')  
    # amount = data.get('amount')
    service_id = data.get('serviceId')
    variation_code = data.get('variationCode')

    if not phone_number or not variation_code or not service_id: 
        return jsonify({"error": "Phone number and amount are required"}), 400

    # Call the purchase_product function to interact with VTpass API
    result = purchase_data(phone_number, service_id,variation_code)

    if result:
        return result
# query data transaction status

@app.route('/api/vtpass-data-status', methods=['POST'])
def query_purchase_data_subcription():
    data = request.json
    request_id = data.get("request_id")

    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'request_id':request_id,
        
    }
    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_PURCHASE_DATA_STATUS')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Could query status",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500





if __name__ == "__main__":
    app.run(debug=True)