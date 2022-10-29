import threading
from time import sleep
import json
from datetime import datetime, timedelta
from urllib import request
from utils.utilities import Command, generateDataFrame
from utils import sushi


class SensorMonitor:
    def __init__(self, serialService, mqttclient, dbpath:str):
        '''
            nodes: list([int(nodeId), int(T_monitor)])
                nodeId      -> node ID (1 to 255)
                T_monitor   -> Time period to execute monitoring
        '''
        self.comm = serialService
        self.mqttclient = mqttclient
        self.db_path = dbpath
        self.db = sushi.sushiWrapper()

        # Monitor Routine
        self.run = False
        self.db_queue = []
        self.db_response = {}
        self.thd_service = threading.Thread(target=self.service, daemon=True).start()
        self.thd_dbService = threading.Thread(target=self.db_service, daemon=True).start()
        self.comm.listener.start()
    
    def db_service(self):
        '''
            TODO: This service could be written in separated process
        '''
        self.db.open(f'{self.db_path}/sensorlog.db')
        while True:
            try:
                command = self.db_queue.pop(0)
                # print(command['command'])
                if command['command'] == 'logsensor':
                    request_id = command['request_id']
                    column = command['column']
                    value = command['value']
                    
                    if self.db.isExist(f'node_{request_id}'):                          # STORE TO DB
                        dtype = ('TEXT', 'INT', 'INT', 'INT', 'INT', 'INT')
                        self.db.createTable(f'Node_{request_id}', column, dtype)
                    self.db.insertOne(
                        tablename=f'Node_{request_id}', 
                        rowname = column, 
                        rowdata = value
                        )
                    self.db.commit()

                elif command['command'] == 'getdata':                                   
                    print('MASUK')
                    request_id = command['request_id']
                    start = command['start']
                    end = command['end']

                    try:
                        firstrecord = self.db.select(f'Node_{request_id}', 'id' , 1, '*')[0][1]
                        lastrecord = self.db.getLastRecord()[0][1]
                        result = self.db.selectBetween(f'Node_{request_id}','Timestamp',start, end)
                        self.db_response = {
                            'request':{'request start':start, 'request end':end, 'nodeid':request_id},
                            'status':{
                                'first timestamp':firstrecord,
                                'last timestamp':lastrecord,
                            },
                            'result':result
                        }
                    except:
                        self.db_response = {
                            'request':{'request start':start, 'request end':end, 'nodeid':request_id},
                            'status':{
                                'first timestamp':0,
                                'last timestamp':0,
                            },
                            'result':"NA"
                        }
            except Exception as e:
                # print(str(e))
                pass
            sleep(0.2)

    def service(self):
        print('Service STARTED')
        self.run = True
        while True:
            data = self.comm.getQueue()                                              # NOTE: Data is parsed data
            if not self.run:
                sleep(0.2)
                continue
            if data == []:
                pass
            else:
                request_id = data['source_addr']
                control_type = data['control']
                information = ''.join([chr(i) for i in data['information']])
                if control_type == Command.action:
                    try:
                        information = json.loads(information)
                        topic = json.dumps(information['topic'])
                        value = information['values']
                        if information['command'] == 'publish':
                            self.mqttclient.publish(topic, json.dumps(value))                           # MQTT PUBLISH
                            

                            db_command = {
                                'command':'logsensor',
                                'request_id':request_id,
                                'column' : ('Timestamp', 'Sensor_1', 'Sensor_2', 'Sensor_3', 'Sensor_4', 'Sensor_5'),
                                'value' : tuple([datetime.now().strftime("%m/%d/%Y %H:%M:%S")]+[value[i] for i in value]),
                            }
                            self.db_queue.append(db_command)
                            # self.db.open(f'{self.db_path}/sensorlog.db')                                # STORE TO DATA BASE. NOTE: Could be multiple access
                            # column = ('Timestamp', 'Sensor_1', 'Sensor_2', 'Sensor_3', 'Sensor_4', 'Sensor_5')
                            # if self.db.isExist(f'node_{request_id}'):                          # STORE TO DB
                            #     dtype = ('TEXT', 'INT', 'INT', 'INT', 'INT', 'INT')
                            #     self.db.createTable(f'Node_{request_id}', column, dtype)
                            # self.db.insertOne(
                            #     tablename=f'Node_{request_id}', 
                            #     rowname = column, 
                            #     rowdata = tuple([datetime.now().strftime("%m/%d/%Y %H:%M:%S")]+[value[i] for i in value]))
                            # self.db.commit()
                            # self.db.close(f'{self.db_path}/sensorlog.db')
                                
                            dataframe = generateDataFrame(0, request_id, Command.ack, "OK") # SEND ACK TO NODE
                            self.comm.write(dataframe)
                    except:
                        dataframe = generateDataFrame(0, request_id, Command.ack, "NA")
                        self.comm.write(dataframe)
            sleep(0.2)

    def start(self) -> bool:
        if not self.run:
            self.run = True
            return True
        return False

    def stop(self) -> bool:
        self.run = False
        return True