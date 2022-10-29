from paho.mqtt import client as mqtt
import json

class MQTTService:
    def __init__(self, brokerAddress, brokerPort) -> None:
        self.brokeraddress = brokerAddress
        self.brokerport = brokerPort

       # CREATE MQTT CLIENT
        self.client = mqtt.Client()
        self.client.connect(brokerAddress, brokerPort)

        # COFIG PUBLISH SUBSCRIBE 
        self.client.on_connect = self.onConnected
        self.client.on_message = self.onDataReceived
        
        # START CLIENT
        self.client.loop_start()

    # CALLBACK FUNCTIONS
    # On connection state
    def onConnected(self,client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.client.subscribe('request')
        else:
            print("Failed to connect, return code %d\n", rc)
            exit()

    # On data received
    def onDataReceived(self, client, userdata, message):
        '''
            Expected data is JSON string contain key id, command, and data. If data received is valid, the the request comand will be append to request queue, else response EROR message
        '''
        print('GET DATA')
        try:
            payload = str(message.payload.decode('utf-8'))
            payload = json.loads(payload)
        except:
            print('Error payload not JSON')
            client.publish("response",'{"result":"ERROR!. payload not JSON"}')
        
    def publish(self,topic:str, payload:str)->None:
        '''
            payload shall be bytearray
        '''
        # print(f'publish -- {topic} -- {payload}')
        self.client.publish(topic,payload)