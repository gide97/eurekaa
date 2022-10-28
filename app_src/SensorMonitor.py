import threading
from time import sleep
import json
from datetime import datetime, timedelta
from utils import sushi


class MonitorTiming():
    '''
        Helper to manage serial event state
    '''

    def __init__(self, period:int) -> None:
        '''
            period: (uint) in second
        '''
        self.t_prev = datetime.now()
        self.period = period

    def updateLastState(self):
        self.t_prev = datetime.now()
    
    def isReady(self):
        return True if datetime.now()-self.t_prev > timedelta(seconds=self.period) else False
    
class SensorMonitor:
    def __init__(self, nodes:list, serialRouter, mqttclient, dbpath:str):
        '''
            nodes: list([int(nodeId), int(T_monitor)])
                nodeId      -> node ID (1 to 255)
                T_monitor   -> Time period to execute monitoring
        '''
        self.nodes = [[node, MonitorTiming(T_period)] for node,T_period in nodes]           # re format node to add individual state
        self.comm = serialRouter
        self.mqttclient = mqttclient
        self.db_path = dbpath
        self.db = sushi.sushiWrapper()

        # Monitor Routine
        self.run = False
        self.thd_service = threading.Thread(target=self.monitor, daemon=True)
        self.initial()

    def initial(self):
        # Create database connection and table initialization
        for idx,node in enumerate([node[0] for node in self.nodes]):
            self.db.open(f'{self.db_path}/sensorlog.db')
            try:  
                self.db.select(f'Node_{node}')                               # NOTE: Will return exception if table does not exist
            except:
                column = ('Timestamp', 'Sensor_1', 'Sensor_2', 'Sensor_3', 'Sensor_4', 'Sensor_5')
                dtype = ('TEXT', 'INT', 'INT', 'INT', 'INT', 'INT')
                self.db.createTable(f'Node_{node}', column, dtype)
            self.db.close()

    def logSensor(self, nodeId):
        self.db.open(f'{self.db_path}/sensorlog.db')
        isValid, _raw, parsedData = self.comm.getData(nodeId)
        if isValid:
            #TODO: [1] log data to db, [2] MQTT publish
            # [1]
            try:
                data = ''.join([chr(i) for i in parsedData['information']])       # NOTE: data sent by node is JSON string. Parse it with json::loads
                data = json.loads(data)
            except:
                return 'Invalid data from sensor'
        
            # self.db.insertOne('Node_1', tuple(['Timestamp']+[f'Sensor_{x+1}' for x in range(0,5)]), tuple([datetime.now().strftime("%m/%d/%Y %H:%M:%S")]+[data[i] for i in data]))
            # self.db.commit()
            # self.db.close()
            # [/1]

            # [2] 
            # NOTE: dummy data topic
            self.mqttclient.publish('sensor_0', json.dumps(data))
            for idx, _key in enumerate(data):                                                      # NOTE: data is in dict
                self.mqttclient.publish(f'sensor_{idx+1}', f'{data[_key]}')
            # [/2]
            return data
        else:
            return 'Something unexpected when reading sensor'

    def monitor(self):
        while self.run:
            for node in self.nodes:                                                 # TODO: Pooling sensor read 
                nodeId, nodeState = node
                if nodeState.isReady():
                    print(f'Reading sensor {nodeId}')
                    self.logSensor(nodeId)
                    nodeState.updateLastState()
            sleep(0.2)
                
    def start(self) -> bool:
        if not self.run:
            self.run = True
            self.thd_service = threading.Thread(target=self.monitor, daemon=True)
            self.thd_service.start()
            return True
        return False

    def stop(self) -> bool:
        self.run = False
        return True