from time import sleep
from flask import Flask, render_template, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import pathlib
import os
import json
from datetime import datetime, timedelta

# from utils import sushi
from utils.SerialListener import SerialListener
from SensorMonitor import SensorMonitor
from MQTTservice import MQTTService

APP_DATA_PATH       = f'{pathlib.Path(__file__).parent.absolute()}/appdata'
DB_PATH             = f'{APP_DATA_PATH}/db'
APP_CONFIG_PATH     = f'{APP_DATA_PATH}/config.txt'

MQTT_BROKER_ADDR    = '192.168.0.105'
MQTT_BROKER_PORT    = 1883

SERIAL_COMM_PORT    = 'COM31'
BAUD_RATE           = 115200

DB_TIMEOUT          = 3 # in second

# Directory Initialization
if not os.path.exists(APP_DATA_PATH):
    os.mkdir(APP_DATA_PATH)
if not os.path.exists(DB_PATH):
    os.mkdir(DB_PATH)

# Create connection to nodes
comm = SerialListener(SERIAL_COMM_PORT, BAUD_RATE)

# MQTT SERVICE
mqtt_client = MQTTService(brokerAddress=MQTT_BROKER_ADDR, brokerPort=MQTT_BROKER_PORT)                                                    # NOTE: Auto connect to broker

# Main Routine                                                        # NOTE: Monitor sensor each T sec
monitor = SensorMonitor(comm, mqtt_client, DB_PATH)


# WEB Server Creation
app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/static/docs/docs.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        'app_name' : 'Eureka API docs'
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/startservice')
def startservice():
    global monitor
    try:
        if monitor.start():
            return jsonify({'response':'OK'})
        return jsonify({'response':'Already Running'})
    except Exception as e:
        return jsonify({'response':f'Error occurs when starting service. Error message {str(e)}'})

@app.route('/stopservice')
def stopservice():
    global monitor
    if not monitor.run:
        return jsonify({'response':'service stopped'})
    try:
        monitor.run = False
    except Exception as e:
        return jsonify({'response': f'Exception occurs with message {str(e)}'})
    return jsonify({'response':'OK'})

@app.route('/checkmqtt')
def monitormqtt():
    return render_template('mqtt.html')

@app.route('/serverstatus')
def getappconfig():
    resp = {
        'MQTT_Broker':f'{MQTT_BROKER_ADDR}:{MQTT_BROKER_PORT}',
        'Serial Port':[SERIAL_COMM_PORT],
        'Service status':["RUNNING" if monitor.run else "STOPPED"],
    }
    return jsonify(resp)

@app.route('/getdb')
def getDB():
    arg = request.args.to_dict()
    try:
        payload = {
            'command': 'getdata',
            "request_id" : int(arg['nodeid']),
            'start' : arg['start'],
            'end' : arg['end']
        }
        monitor.db_response = {}
        monitor.db_queue.append(payload)
        t1 = datetime.now()
        while datetime.now() - t1 < timedelta(seconds=DB_TIMEOUT):
            if monitor.db_response != {}:
                _temp = monitor.db_response
                monitor.db_response = {}
                return jsonify(_temp)
            sleep(0.1)
        return '400'
    except:
        return '400'   


@app.route('/appconfig')
def appconfig():
    '''
        mqtt broker address
        mqtt broker port

        rf transciever serial port
    '''
    return render_template('appsetting.html')