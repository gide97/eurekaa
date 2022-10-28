import threading
from time import sleep
import serial
import json
from datetime import datetime, timedelta

from .utilities import Command, CRC, generateDataFrame

class SerialRouter:
    def __init__(self, serialPort:str, baudRate:int):
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

    def transaction(self, data:bytearray, timeout:int=2)->list:
        '''
            Send data and wait ack from sensor until 
        '''
        # tx data
        self.ser.write(data)
        
        # rx data
        recv_buffer = []
        flag_recieving = False
        t_time = datetime.now()
        while datetime.now() - t_time < timedelta(seconds=timeout):     # Wait data stream 
            recv_data = self.ser.read().hex()
            if len(recv_data) > 0:                                      # Receiving data stream
                if recv_data == '7e':
                    flag_recieving = True
                t_time = datetime.now()
                recv_buffer.append(int(recv_data,16))
            else:                                                       # When data stream is over
                if flag_recieving: 
                    return recv_buffer                                  # TODO: Authenticate data with checksum
        return []                                                       # Timeout
        
        
    # Refer to documentation :: data link format 
    def getData(self, nodeId:int, information:bytearray=None) -> tuple:
        '''
            Get data from node

            Params:
            nodeId      : 1 to 255. 0 only for supervisor
            attribute   : [ OPTIONAL ] Additional information

            return value: tuple (<bool>isvalid, <list>raw data, <dict> data scape)
        '''
        dataframe = generateDataFrame(0, nodeId, Command.read, information)
        ack = self.transaction(dataframe)
        isValid, ack, data = CRC.verify(ack)
        return isValid, ack, data

    def writeData(self, nodeId:int, information:bytearray) -> tuple:
        '''
            Set command to node

            Params:
            nodeId          : 1 to 255. 0 only for supervisor
            information     : Additional information written in json string

            return value: tuple(<bool>isValid, <list>raw data, <dict> data scape)
        '''
        dataframe = generateDataFrame(0, nodeId, Command.write, information)
        ack = self.transaction(dataframe)                                   # TODO: Verify before return the data
        isValid, ack, data = CRC.verify(ack)
        return isValid, ack, data
    
    def pingNode(self, nodeId:int) -> bool:
        '''
            PING the node
            nodeId      : 1 to 255. 0 only for supervisor
        '''
        dataframe = generateDataFrame(0, nodeId, Command.ping)
        ack = self.transaction(dataframe)
        isValid, data = CRC.verify(ack)
        return isValid, ack, data