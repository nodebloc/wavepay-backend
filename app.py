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

cableServiceId ={
        "dstv": "dstv",
        "gotv": "gotv",
        "startimes": "startimes"
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
@app.route('/api-verify-transaction-status', methods=['POST'])
def check_transaction_status():
    header = {'api-key': API_KEY,'public-key': PUBLIC_KEY,'secret-key': SECRET_KEY}
    try:
        
        
        # VTpass transaction status endpoint
        url = "https://sandbox.vtpass.com/api/requery"
        
        # Payload with the request_id
        # try and set this dynamically
        payload = {
            "request_id": "202410070901IXNUbX6aPL"
        }
        
        # Send POST request to VTpass with basic auth
        response = requests.post(url, json=payload, headers = header)
        
        # Get the JSON response
        data = response.json()
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
# Data subcription
@app.route('/api-get-data-variation-code', methods=['GET'])
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


#Cable Subcription
#Getting variation code
@app.route('/api/get-cable-variation-code', methods=['GET'])
def get_variation_cable__codes():
    
    cable= request.json  
    cableId = cable.get('cableType')  
    url = os.getenv("VT_SANDBOX_URL_CABLE_VARIATION_CODE")
    url="{}{}".format(url,cableServiceId[cableId])
    response = requests.get(url, headers = headers)
    data = response.json()
    
    return jsonify(data)

@app.route('/api/vtpass-verify-Smartcard', methods=['POST'])
def verify_card():
    data = request.json
    cardNumber= data.get("cardNumber")
    serviceId = data.get("serviceID")

    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'billersCode':cardNumber,
        'serviceID':serviceId
        
    }
    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_VERIFY_SMART_CARD')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Could not verify Smart Card",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500

# Bouque change for 
@app.route('/api/vtpass-cablesubscription', methods=['POST'])
def subcribe_bouquetChange():
    data = request.json
    serviceID = data.get("serviceID")
    billersCode = data.get("billersCode")
    variation_code = data.get("variation_code")
    amount = data.get("amount")
    phone = data.get("phone")
    subscription_type = data.get("subscription_type")
    quantity = data.get("quantity")

    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    requestID = generate_request_id()

    # Payload (data) that will be sent to VTpass API
    payload = {
        'request_id':requestID,
        'serviceID': serviceID,
        'billersCode': billersCode,
        'variation_code': variation_code,
        'amount': amount,
        'phone': phone,
        'subscription_type': subscription_type,
        'quantity':quantity

    }
    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_BOUQUET_CHANGE')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            # data = response.json()
            # return {
            #     "data": data,
            #     "req": requestID
            # }

            data = response.json()

            if data['code'] == "000":
                
                return {
                    "data": data,
                    "req": requestID
                }
            else:
                return {
                    "status": False,
                    "error": data['content']['errors'],
                    "message": "Error",
                    "reason": "Failed to renew cable subscription"
                }
        else:
            return jsonify({
                "error": "Could query status", "req": requestID,
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "req": requestID, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500

# verify prepaid/post  metercard Number
@app.route('/api/vtpass-verify-meterNumber', methods=['POST'])
def verify_meterNumber():
    data = request.json
    meterNumber= data.get("billersCode")
    serviceId = data.get("serviceID")
    metertype = data.get("type")

    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'billersCode':meterNumber,
        'serviceID':serviceId,
        'type':metertype
        
    }
    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE = os.getenv('VT_SANDBOX_URL_METER_VERIFY')
        response = requests.post(VT_SANDBOX_URL_PURCHASE, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Invalid meter Number",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500


# Purchase  prepaid/post  meter(Electricity)
@app.route('/api/vtpass-purchaseElectricity', methods=['POST'])
def purchase_electricity():
    data = request.json
    amount = data.get("amount")
    phone=data.get("phone")
    meterNumber= data.get("billersCode")
    serviceId = data.get("serviceID")
    variation_code =data.get("variation_code")

    headers = {
         'api-key': API_KEY,
         'secret-key': SECRET_KEY,
         'Content-Type': 'application/json' 
        
    }

    # Payload (data) that will be sent to VTpass API
    payload = {
        'request_id': generate_request_id(),
        'billersCode':meterNumber,
        'serviceID':serviceId,
        'variation_code': variation_code,
        'amount': amount,
        'phone':phone
       
        
    }
    try:
        # Make a POST request to VTpass API
        VT_SANDBOX_URL_PURCHASE_ELECTRICITY = os.getenv('VT_SANDBOX_URL_PURCHASE_ELECTRICTY')
        response = requests.post(VT_SANDBOX_URL_PURCHASE_ELECTRICITY, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()  
            return data
        else:
            return jsonify({
                "error": "Invalid meter Number",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code
        # return response.json() 
    except Exception as e:
        return jsonify({"status": False, "message": "Could not connect to the apiendpoint", "error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)