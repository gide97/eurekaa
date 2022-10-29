# Prerequest:
1. Install Python 3.xx
2. MQTT broker (use Mosquitto for offline broker)
3. 2 RD module (I use 2 USB TTL to simulate HC12 RF module)

# Script structure
1. app_src -> script for main device (Forwarder Node)
2. sensor_src -> script for sensor node 

Thus, we need to use 2 terminals to simulate the firmware

# Running firmware
For *Main Device* node:
1. enter app_src
2. create python virtual environment
3. enter virtual environment in Linux: `source env/bin/activate` 
4. install requirements.txt with `pip install -r requirements.txt`
5. configure server on app_src/appdata/config.json. *For detail refer to wiki*
6. run server with run `flask run`

For *Sensor Node*, using new terminal:
1. enter sensor_src
2. create python virtual environment `pip install -r requirements.txt`
3. enter virtual environment in Linux: `source env/bin/activate` 
4. install requirements.txt `pip install -r requirements.txt`

# Details
Please refer to wiki
