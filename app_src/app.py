from flask import Flask, render_template, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import pathlib
import os
import json
from datetime import datetime

# from utils import sushi
from utils.SerialRouter import SerialRouter
from SensorMonitor import SensorMonitor
from MQTTservice import MQTTService

APP_DATA_PATH       = f'{pathlib.Path(__file__).parent.absolute()}/appdata'
DB_PATH             = f'{APP_DATA_PATH}/db'
APP_CONFIG_PATH     = f'{APP_DATA_PATH}/config.txt'

MQTT_BROKER_ADDR    = '10.23.16.33'
MQTT_BROKER_PORT    = 1883

SERIAL_COMM_PORT    = 'COM8'

# Directory Initialization
if not os.path.exists(APP_DATA_PATH):
    os.mkdir(APP_DATA_PATH)
if not os.path.exists(DB_PATH):
    os.mkdir(DB_PATH)

# Create connection to nodes
nodes = [1,2]                                                         # TODO: Add another node inside the list
comm = SerialRouter(SERIAL_COMM_PORT, 9600)

# MQTT SERVICE
mqtt_client = MQTTService(brokerAddress=MQTT_BROKER_ADDR, brokerPort=MQTT_BROKER_PORT)                                                    # NOTE: Auto connect to broker

# Main Routine
_T_MONITOR = 2                                                        # NOTE: Monitor sensor each T sec
monitor = SensorMonitor([[node, _T_MONITOR] for node in nodes], comm, mqtt_client, DB_PATH)
# monitor.start()

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

@app.route('/nodelist')
def getNodeList():
    resp = {
        'num_of_sensor' : len(nodes),
        'sensor_id'     : nodes
    }
    return jsonify(resp)

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
    if not monitor.thd_service.isAlive():
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
        'Service status':["RUNNING" if monitor.thd_service.isAlive() else "STOPPED"],
        'Sensor Node list':nodes
    }
    return jsonify(resp)

@app.route('/appconfig')
def appconfig():
    '''
        mqtt broker address
        mqtt broker port

        rf transciever serial port
    '''
    return render_template('appsetting.html')