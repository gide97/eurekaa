# Prerequest:
1. Install Python 3.xx
2. MQTT broker (use Mosquitto for offline broker)

# Script structure
1. app_src -> script for main device (Forwarder Node)
2. sensor_src -> script for sensor node 

Later, to simulate firmware functionality we need to use 2 terminals.


# Running firmware
For *Main Device* node:
1. enter app_src
2. create python virtual environment
3. install requirements.txt
4. configure server on app_src/appdata/config.json. *For detail refer to wiki*
5. run server with run `flask run`

For *Sensor Node*, using new terminal:
1. enter sensor_src
2. create python virtual environment
3. install requirements.txt

