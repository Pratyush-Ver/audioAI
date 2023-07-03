import paho.mqtt.client as mqtt
import json
from time import sleep
from datetime import datetime
import requests
import os
import threading

#Recording Path Variable
audioFile = '/home/raspberry/processed/'

#Cloud Variables
cloudConfigFile = '/home/raspberry/cloud_client/config_files/cloud.json'
mqttBroker = ''
port = 9999
reqConfTopic = ''
reqFileTopic = ''
respConfTopic = ''
respFileTopic = ''
rootCA="/home/raspberry/cert/AmazonRootCA1.pem"
cert="/home/raspberry/cert/certificate.pem.crt"
key="/home/raspberry/cert/private.pem.key"

#Device Variables
deviceConfigFile = '/home/raspberry/cloud_client/config_files/device.json'
devId = ''

#Sound Variables
soundConfigFile = '/home/raspberry/cloud_client/config_files/sound.json'

#gps Variables
gpsDataFile = '/home/raspberry/cloud_client/config_files/gps.json'


def json_reader(file):
    with open(file,'r') as outfile:
        data = json.load(outfile)
    return data

def cloud_config():
    global mqttBroker
    global port
    global reqConfTopic 
    global reqFileTopic
    global respConfTopic 
    global respFileTopic 
    val = json_reader(cloudConfigFile)
    mqttBroker = val['endpointUrl']
    port = val['port']
    reqConfTopic = val['reqConfigTopic']+'/'+devId
    reqFileTopic = val['reqFileTopic']+'/'+devId
    respConfTopic = val['respConfigTopic']+'/'+devId
    respFileTopic = val['respFileTopic']+'/'+devId

def device_config():
    global devId
    val = json_reader(deviceConfigFile)
    devId = val['deviceId']

def build_config_payload():
    dt = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    dev_val = json_reader(deviceConfigFile)
    cloud_val = json_reader(cloudConfigFile)
    sound_val = json_reader(soundConfigFile)
    payload = {
        "deviceId":devId,
        "timeStamp":dt,
        "msgType":"response",
        "config": {
            "device":dev_val,
            "cloud":cloud_val,
            "sound":sound_val
            }
        }
    print(payload)    
    return json.dumps(payload)

def audio_upload_ack_payload(data,status):
    dt = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    payload = {
        "deviceId":devId,
        "timeStamp":dt,
        "requestType":data['requestType'],
        "requestValue":data['requestValue'],
        "status":status
        }
    return json.dumps(payload)

def audio_upload(client, val):
    file = audioFile + val['requestValue']
    if os.path.isfile(file):
        print('file_exists')
        response = val['uploadUrl']
        files = { 'file': open(file, 'rb')}
        r = requests.post(response['url'], data=response['fields'], files=files)
        resp_code = r.status_code
        if resp_code == 204:
            payload = audio_upload_ack_payload(val,"Uploaded")
            client.publish(respFileTopic,payload,0) 
        else:
            payload = audio_upload_ack_payload(val,"Not Uploaded")
            client.publish(respFileTopic,payload,0) 
    else:
        print('file not found')
        payload = audio_upload_ack_payload(val,"File not found")
        client.publish(respFileTopic,payload,0) 

def publish_config(client,userdata,message):
    val = json.loads(message.payload.decode('utf-8'))
    print(val)
    if val['deviceId'] == devId:
        print('Valid read config Request')
        payload = build_config_payload()
        client.publish(respConfTopic,payload,0)
    else:
        print('Invalid Request!!!')

def audio_request(client, userdata, message):
    val = json.loads(message.payload.decode('utf-8'))
    thAudio = threading.Thread(target=audio_upload, args=(client, val))
    thAudio.start()

def build_ping_payload():
    dt = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    payload = {
        "deviceId":devId,
        "timeStamp":dt
        }
    return json.dumps(payload)

device_config()
cloud_config()

    
mqttClient = "req"+devId
client = mqtt.Client(mqttClient)
client.tls_set(rootCA,cert,key)

MQTT_KEEPALIVE_INTERVAL = 45

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(reqConfTopic,0)
        client.subscribe(reqFileTopic,0)
        payload = build_config_payload()
        client.publish(respConfTopic,payload,0)
    else:
        Connected = False
        print("Connection failed")


client.on_connect = on_connect
client.message_callback_add(reqConfTopic,publish_config)
client.message_callback_add(reqFileTopic,audio_request)

try:
    client.connect(mqttBroker, port, MQTT_KEEPALIVE_INTERVAL)
except:
    print("Did not connect")


client.loop_start()


while True:
    print("------Active---")
    sleep(20)
            

    
