import threading
import serial
import json
import time
from datetime import datetime, timedelta
from random import randint
from utils.utilities import CRC, Command, generateDataFrame

class Node:
    def __init__(self, serialPort:str, baudRate:int, nodeId:int=None)->None:
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
        threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.sensor_measurement, daemon=True).start()

    def apiCall(self, api, data):
        return self.api[api](data)

    def handler_wellknown(self) -> str:
        payload = list(self.api.keys())
        return payload

    def handler_ping(self) -> str:
        return 'pong'

    def handler_read(self) -> str:
        return json.dumps(self.sensorvalues)
    
    def handler_write(self) -> str:
        return f'OK'

    # Sensor metrology
    def sensor_measurement(self) -> str:
        while True:
            for i in range(0,5):
                self.sensorvalues[f'sensor {i+1}'] = randint(0,100)
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