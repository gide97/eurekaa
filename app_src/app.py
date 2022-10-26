from flask import Flask, render_template, jsonify
from paho import mqtt
import pathlib
import os
import json

from utils import sushi
from utils.SensorMonitor import SensorMonitor

APP_DATA_PATH       = f'{pathlib.Path(__file__).parent.absolute()}/appdata'
DB_PATH             = f'{APP_DATA_PATH}/db'
APP_CONFIG_PATH     = f'{APP_DATA_PATH}/config.txt'

if not os.path.exists(APP_DATA_PATH):
    os.mkdir(APP_DATA_PATH)
if not os.path.exists(DB_PATH):
    os.mkdir(DB_PATH)

app = Flask(__name__)
monitor = SensorMonitor('COM8', 115200)

# Database Configuration
db = sushi.sushiWrapper()

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/logsensor')
def logsensor():
    _, raw, data = monitor.getData(1)
    
    
    db.open(f'{DB_PATH}/sensorlog.db')
    try:
        print(db.select('log'))
    except:
        db.createTable('log', )
    db.close()
    return data['information']