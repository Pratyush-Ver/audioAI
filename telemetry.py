import paho.mqtt.client as mqtt
import json
from time import sleep
from datetime import datetime
from ipcqueue import posixmq

q = posixmq.Queue("/detect") #ipc queue object

#Cloud Variables
cloudConfigFile = '/home/raspberry/cloud_client/config_files/cloud.json'
mqttBroker = ''
port = 9999
telTopic = ''
pingTopic = ''
rootCA="/home/raspberry/cert/AmazonRootCA1.pem"
cert="/home/raspberry/cert/certificate.pem.crt"
key="/home/raspberry/cert/private.pem.key"

#Device Variables
deviceConfigFile = '/home/raspberry/cloud_client/config_files/device.json'
devId = ''
devType = ''

#Sound Variables
soundConfigFile = '/home/raspberry/cloud_client/config_files/sound.json'
recDuration = 0
recFormat = ''
recSamplingRate = 0
onsetThreshold = 0

#gps Variables
gpsDataFile = '/home/raspberry/cloud_client/config_files/gps.json'
lat = 0.0
long = 0.0



def json_reader(file):
    with open(file,'r') as outfile:
        data = json.load(outfile)
    return data

def cloud_config():
    global mqttBroker
    global port
    global telTopic
    global pingTopic
    val = json_reader(cloudConfigFile)
    mqttBroker = val['endpointUrl']
    port = val['port']
    telTopic = val['telemetryTopic']
    pingTopic = val['pingTopic']

def device_config():
    global devId
    global devType
    val = json_reader(deviceConfigFile)
    devId = val['deviceId']
    devType = val['deviceType']

def sound_config():
    global recDuration
    global recFormat
    global recSamplingRate
    global onsetThreshold
    val = json_reader(soundConfigFile)
    recDuration = val['recDuration']
    recFormat = val['recFormat']
    recSamplingRate = val['recSamplingRate']
    onsetThreshold = val['onsetThreshold']

def gps_data():
    global lat
    global long
    val = json_reader(gpsDataFile)
    lat = val['lat']
    long = val['long']


def build_telemetry_payload():
    dt = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    #fn = dt + '.wav'
    if q.qsize() > 0:
        val = q.get()
        fn=val["recFileName"]
        detection_count=val["detectionCount"]
        peak_timestamp=val["peakTimeStamp"]
        peak_magnitudes=val["peakMagnitude"]
    payload = {
        "deviceId":devId,
        "deviceType":devType,
        "timeStamp":dt,
        "recTimeStamp":(fn.split("_")[1]).split(".")[0],
        "recFileName":fn,
        "gpsLat":lat,
        "gpsLong":long,
        "recDuration":recDuration,
        "recSamplingRate":recSamplingRate,
        "recFormat":recFormat,
        "detectionCount":detection_count, 
        "onsetThreshold":onsetThreshold,
        "peakTimeStamp":peak_timestamp,
        "peakMagnitude":peak_magnitudes
        }
    return json.dumps(payload)

def build_ping_payload():
    dt = datetime.now().strftime("%d-%m-%YT%H-%M-%S")
    payload = {
        "deviceId":devId,
        "timeStamp":dt,
        "msgType":"heartbeat"
        }
    return json.dumps(payload)


cloud_config()
device_config()
sound_config()
    

mqttClient = "tel"+devId
client = mqtt.Client(mqttClient)
client.tls_set(rootCA,cert,key)

MQTT_KEEPALIVE_INTERVAL = 45

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker") 
        print("sucessfully subscribed")
    else:
        Connected = False
        print("Connection failed")


client.on_connect = on_connect

try:
    client.connect(mqttBroker, port, MQTT_KEEPALIVE_INTERVAL)
except:
    print("Did not connect")

client.loop_start()

while True:
    gps_data()
    if q.qsize() > 0:
        tel_payload = build_telemetry_payload()
        client.publish(telTopic,tel_payload)
    ping_payload = build_ping_payload()
    #client.publish(telTopic,tel_payload)
    client.publish(pingTopic,ping_payload)
    sleep(20)

            

    
