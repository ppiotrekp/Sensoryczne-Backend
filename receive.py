from flask import Flask, jsonify, request
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import pandas as pd
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Dodanie filtru CORS

ENDPOINT = "al262i83u5jf3-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "testDevice2"
PATH_TO_CERTIFICATE = "certificates/certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certificates/private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/AmazonRootCA1.pem"
MESSAGE = "Hello World"
TOPIC = "device/TEMP_BPM_SO2"
RANGE = 20

myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)

myAWSIoTMQTTClient.connect()

last_message = None

def on_message(client, userdata, message):
    global last_message
    last_message = json.loads(message.payload)

myAWSIoTMQTTClient.subscribe(TOPIC, 1, on_message)

@app.route('/last_message', methods=['GET'])
def get_last_message():
    if last_message is not None:
        formatted_message = {
            "temperature": float(last_message["data"][0]),
            "saturation": int(last_message["data"][1]),
            "bmp": int(last_message["data"][2])
        }
        return jsonify(formatted_message)
    else:
        return "No messages yet", 404


model = joblib.load('/home/ppryczak/SENSORYCZNE/modelML/bestmodel.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    updated_data = {
        "Puls": data["bpm"],
        "Temperatura": data["temperature"],
        "Saturacja krwi": data["saturation"]
    }

    df = pd.DataFrame(updated_data, index=[0])

    prediction = model.predict(df)

    result = {'prediction': prediction.tolist()}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

