import threading
import serial
import json
import time
from datetime import datetime, timedelta
from random import randint
from utils.utilities import CRC, Command, generateDataFrame

class Node:
    def __init__(self, serialPort:str, baudRate:int, nodeId:int)->None:
        self.serialPort = serialPort
        self.baudRate = baudRate
        self.id = nodeId
        

        self.ser = serial.Serial(
            port = serialPort,
            baudrate = baudRate,
            parity = serial.PARITY_NONE,
            bytesize = serial.EIGHTBITS,
            stopbits = serial.STOPBITS_ONE,
            timeout = 0.1
        )

        # sensor metrology
        self.sensorvalues = {
            'sensor 1':0,
            'sensor 2':0,
            'sensor 3':0,
            'sensor 4':0,
            'sensor 5':0,
        }

        # node apis
        self.api = {
            'wellknown-core': self.handler_wellknown,
            'ping'          : self.handler_ping,
            'read'          : self.handler_read,
            'write'         : self.handler_write,           
        }


        # node routine system
        self.serialTimeout = 5
        self.sampleMeasurementRate = 1                                                      # Time period for read sensor
        # threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.sensor_measurement, daemon=True).start()
    
    def reinit(self):
        self.serialTimeout = 5
        self.sampleMeasurementRate = 1

    def apiCall(self, api, data):
        return self.api[api](data)

    def handler_wellknown(self) -> str:
        payload = list(self.api.keys())
        return payload

    def handler_ping(self) -> str:
        return 'pong'

    def handler_read(self) -> str:
        return json.dumps(self.sensorvalues)
    
    def handler_write(self, data:list) -> str:
        try:
            data = ''.join([chr(i) for i in data])
            data = json.loads(data)
            if data['command'] == 'sampling_rate':  # SET MEASUREMENT SAMPLING RATE
                self.sampleMeasurementRate == data['value']
            if data['command'] == 'reset':          # SET NODE CONFIGURATION TO DEFAULT
                self.reinit()
        except:
            return f'NA'

        return f'OK'

    # Sensor metrology
    def sensor_measurement(self) -> str:
        while True:
            for i in range(0,5):
                self.sensorvalues[f'sensor {i+1}'] = randint(0,100)

                # Request to publish sensors value
                buffer = generateDataFrame(self.id, 0, Command.action, json.dumps({"command":"publish", "topic":f"sensor_{self.id}", "values":self.sensorvalues}))
                self.ser.write(buffer)
                time.sleep(self.sampleMeasurementRate)

    # Communication
    def listener(self):
        print(f'Node {self.id} is listening')
        while True:
            
            # rx data
            recv_buffer = []
            isRecieving = False
            t_time = datetime.now()
            while datetime.now() - t_time < timedelta(seconds=self.serialTimeout):          # Wait data stream until timeout
                recv_data = self.ser.read().hex()
                if len(recv_data) > 0:                                                      # Receiving data stream
                    if recv_data == '7e':
                        isRecieving = True
                    t_time = datetime.now()
                    recv_buffer.append(int(recv_data,16))
                else:                                                                       # When data stream is over, execute command
                    if isRecieving: 
                        recv_buffer = bytearray(recv_buffer)
                        break  
                    
            if len(recv_buffer)>0:
                isValid, data = CRC.verify(recv_buffer)                                     # TODO: Verify data frame
                if isValid:
                    if data['destination_addr'] != self.id:                                 # Make sure data is for me
                        continue

                    print(f'Receive New Message: Data control: {data["control"]}')
                    ack = ''
                    if data['control'] == Command.read:
                        print('read command')
                        ack = self.api['read']()
                    elif data['control'] == Command.write:
                        print('write command')
                        ack = self.api['write']()
                    elif data['control'] == Command.ping:
                        print('ping request')
                        ack = self.api['ping']()
                    
                    # response = self.apiCall(data, None)                                  # pass data to API handler
                    response = generateDataFrame(self.id, data['source_addr'], Command.ack, ack)
                    self.ser.write(bytearray(response))                                    # send ack to client

import sys
import getopt
import time

optlist, args = getopt.getopt(sys.argv[1:], 'p:i:b:')
print(optlist)
def reject():
    print('ERROR!! Arguments needed')
    print()
    print('Usage    :')
    print('          python SensorNode.py -p <usb port> -b <baud rate> -i <node id>')
    print('          usb port     : Usb port')
    print('          baud rate    : Baud rate')
    print('          node id      : 1-255')
    print()
    print('Example  : python SensorNode.py -p /dev/ttyUSB1 -i 1')
    exit(1)

_SERIAL_PORT = None
_SERIAL_BAUD_RATE = None
_NODE_ID = None
validation_val = 0x00
for opt in optlist:
    if validation_val == 0x07:
        break
    if '-p' in opt:
        validation_val |= 0x1
        _SERIAL_PORT = opt[1]
    if '-b' in opt:
        validation_val |= 0x2
        _SERIAL_BAUD_RATE = int(opt[1])
    if '-i' in opt:
        validation_val |= 0x4
        _NODE_ID = int(opt[1])
    

if validation_val != 0x07:
    reject()
node = Node(_SERIAL_PORT, _SERIAL_BAUD_RATE, _NODE_ID)
while True:
    time.sleep(1)