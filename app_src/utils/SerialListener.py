import threading
from time import sleep
import serial
import json
from datetime import datetime, timedelta

from .utilities import Command, CRC, generateDataFrame

class SerialListener:
    def __init__(self, serialPort:str, baudRate:int, maxBufferLength:int=1024):
        '''
            nodeId  : 1~255.    0 for supervisor
        '''
        #
        # Serial configuration
        #
        self.serialPort = serialPort
        self.baudRate = baudRate
        self.ser = serial.Serial(
            port = serialPort,
            baudrate = baudRate,
            parity = serial.PARITY_NONE,
            bytesize = serial.EIGHTBITS,
            stopbits = serial.STOPBITS_ONE,
            timeout = 0.1
        )
        self.listener = threading.Thread(target=self.listener_service, daemon=True)
        self.run = False
        self.maxBufferLength = maxBufferLength
        self.queue = []

    def listener_service(self):
        print('Serial listener STARTED')
        self.run = True
        while self.run:
            recv_buffer = []
            flag_recieving = False
            counter = 0
            while self.run:     # Wait data stream 
                recv_data = self.ser.read().hex()
                if len(recv_data) > 0:                                      # Receiving data stream
                    if recv_data == '7e':
                        flag_recieving = True
                    recv_buffer.append(int(recv_data,16))
                    counter += 1
                else:                                                       # When data stream is over
                    if flag_recieving: 
                        isValid, _raw, data = CRC.verify(recv_buffer)
                        if isValid:
                            if data['destination_addr'] == 0:
                                self.queue.append(data)
                        break                                               # TODO: Authenticate data with checksum
                
                if counter>self.maxBufferLength:                                            # NOTE: Protection for unlimited serial stream
                    break
            

    def getQueue(self)->list:
        try:
            data = self.queue.pop(0)
            return data
        except:
            return []

    def startService(self):
        self.listener.start()

    def write(self, buffer:list) -> None:
        '''

        '''
        self.ser.write(buffer)