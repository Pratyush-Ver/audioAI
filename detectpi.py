#----------------------------------------------------------------------------
# Bio-Acoustic Sensor Milestone 1 Detector script
# About:
# >Python based Detector script for sensing onset timings in audio recordings
# Authors:
# >Pratyush Verma
# >Aditya Raj Verma
# ----------------------------------------------------------------------------
import librosa
import librosa.display
#import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime
import os
import time
import tflite_runtime.interpreter as tf
import csv
from ipcqueue import posixmq

q1 = posixmq.Queue('/telemetry',maxmsgsize=8192)
q2 = posixmq.Queue('/notify',maxmsgsize=8192)
print(q1.qattr())


path = "/home/raspberry/rec"
path2 = "/home/raspberry/rec/"
path3 = "/home/raspberry/processed/"

# path = "C:\\Users\\praty\\Desktop\\work\\audioAI\\rec"
# path2 = "C:\\Users\\praty\\Desktop\\work\\audioAI\\rec\\"
# path3 = "C:\\Users\\praty\\Desktop\\work\\audioAI\\temp\\"

# Data to be written
payload = {
"deviceId":"SN0001",
"deviceType":"standalone",
"timeStamp":"dd/mm/yyyy_hh:mm:ss",
"recTimeStamp":"dd/mm/yyyy_hh:mm:ss",
"recFileName":"xyz.wav",
"gpsLat":"11.5N",
"gpsLong":"88.4E",
"recDuration":"10",
"recSamplingRate":"48000",
"recFormat":"wav",
"detectionCount":"11",
"onsetThreshold":"0.01",
"classThreshold":"0.5",
"classType":"all",
"peakTimeStamp":[],
"peakMagnitude":[],
"peakClass":[]
}

q2_payload = {
"deviceId":"SN0001",
"deviceType":"standalone",
"timeStamp":"dd/mm/yyyy_hh:mm:ss",
"recTimeStamp":"dd/mm/yyyy_hh:mm:ss",
"recFileName":"xyz.wav",
"gpsLat":"11.5N",
"gpsLong":"88.4E",
"recDuration":"10",
"recSamplingRate":"48000",
"recFormat":"wav",
"detectionCount":"11",
"onsetThreshold":"0.01",
"classThreshold":"0.5",
"classType":"anomaly",
"peakTimeStamp":[],
"peakMagnitude":[],
"peakClass":[]
}

def build_payload(onset_classes,filename):
    if len(onset_classes)<=0:
        return 
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%YT%H-%M-%S")
    payload["deviceId"]=deviceId
    payload["deviceType"]=deviceType
    payload["gpsLat"]="21.7019"
    payload["gpsLong"]="77.8960"
    payload["timeStamp"]=dt_string
    payload["recFileName"]=filename
    payload["recTimeStamp"]=filename.split("_")[1]
    payload["recDuration"]=recDuration
    payload["recSamplingRate"]=recSamplingRate
    payload["recFormat"]=recFormat
    payload["detectionCount"]=len(onset_classes)
    payload["onsetThreshold"]=threshold
    payload["classThreshold"]=classThreshold
    payload["classType"]="ambient"
    # payload["peakTimeStamp"]=onset_detects
    # payload["peakMagnitude"]=onset_detects_values
    payload["peakClass"]=onset_classes
    json_write(payload)
    print("ambient payload sent")
    print(payload)
    q1.put(payload)

def build_anomaly_payload(onset_classes,filename):
    if len(onset_classes)<=0:
        return
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%YT%H-%M-%S")
    q2_payload["deviceId"]=deviceId
    q2_payload["deviceType"]=deviceType
    q2_payload["gpsLat"]="21.7019"
    q2_payload["gpsLong"]="77.8960"
    q2_payload["timeStamp"]=dt_string
    q2_payload["recFileName"]=filename
    q2_payload["recTimeStamp"]=filename.split("_")[1]
    q2_payload["recDuration"]=recDuration
    q2_payload["recSamplingRate"]=recSamplingRate
    q2_payload["recFormat"]=recFormat
    q2_payload["detectionCount"]=len(onset_classes)
    q2_payload["onsetThreshold"]=threshold
    q2_payload["classThreshold"]=classThreshold
    q2_payload["classType"]="anomaly"
    #q2_payload["peakTimeStamp"]=onset_detects
    #q2_payload["peakMagnitude"]=onset_detects_values
    q2_payload["peakClass"]=onset_classes
    json_write(payload)
    print("anomaly payload sent")
    print(q2_payload)
    q2.put(q2_payload)

def build_unknown_payload(onset_classes,filename):
    if len(onset_classes)<=0:
        return
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%YT%H-%M-%S")
    q2_payload["deviceId"]=deviceId
    q2_payload["deviceType"]=deviceType
    q2_payload["gpsLat"]="21.7019"
    q2_payload["gpsLong"]="77.8960"
    q2_payload["timeStamp"]=dt_string
    q2_payload["recFileName"]=filename
    q2_payload["recTimeStamp"]=filename.split("_")[1]
    q2_payload["recDuration"]=recDuration
    q2_payload["recSamplingRate"]=recSamplingRate
    q2_payload["recFormat"]=recFormat
    q2_payload["detectionCount"]=len(onset_classes)
    q2_payload["onsetThreshold"]=threshold
    q2_payload["classThreshold"]=classThreshold
    q2_payload["classType"]="unknown"
    #q2_payload["peakTimeStamp"]=onset_detects
    #q2_payload["peakMagnitude"]=onset_detects_values
    q2_payload["peakClass"]=onset_classes
    json_write(payload)
    print("unknown payload sent")
    print(q2_payload)
    q2.put(q2_payload)


# Writing to sample.json
def json_write(payload):
    json_object = json.dumps(payload, indent=4)
    with open("/home/raspberry/detections.json", "a") as outfile:
        outfile.write(json_object)

def filecheck():
    dir_list = os.listdir(path)
    print("Files and directories in '", path, "' :")
    print(dir_list)
    if len(dir_list)==0:
        return False, dir_list
    else:
        return True, dir_list

def class_names(class_map_csv):
  """Read the class name definition file and return a list of strings."""
  with open(class_map_csv) as csv_file:
    reader = csv.reader(csv_file)
    next(reader)   # Skip header
    return np.array([display_name for (_, _, display_name) in reader])

def inference(temp_data,filename):
    yamnet_classes = class_names('/home/raspberry/yamnet_class_map.csv')
    #interpreter = tf.lite.Interpreter(model_path="yamnet.tflite")
    interpreter = tf.Interpreter(model_path="/home/raspberry/yamnet.tflite")
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    interpreter.set_tensor(inputs[0]['index'], np.expand_dims(temp_data, axis=0))
    interpreter.invoke()
    scores = interpreter.get_tensor(outputs[0]['index'])
    prediction = np.mean(scores, axis=0)
    top5_i = np.argsort(prediction)[::-1][:1]
    print(filename, ':\n' + 
          '\n'.join('  {:12s}: {:.3f}'.format(yamnet_classes[i], prediction[i])
                    for i in top5_i))
    for i in top5_i:
        onsetclass = yamnet_classes[i]
        onsetpred = '{:.3f}'.format(prediction[i])
    return onsetclass,onsetpred

def detectanomaly(onsetclass,onsetpred,classThreshold):
    ambient=["Silence","Animal","Bird","Frog","Wild animals","Bird vocalization, bird call, bird song","Chirp, tweet","Cat","Meow","Domestic animals, pets","Cattle, bovinae","Pig","Oink","Hiss","Owl"]
    anomaly=["Glass","Wood","Speech","Cough","Chopping (food)","Tools","Filing (rasp)","Rub","Scrape","Chopping (food)","Beep, bleep","Buzzer","Hammer","Engine starting","Sewing machine","Rub","Tools","Sawing","Sanding","Filing (rasp)","Keys jangling","Coin (dropping)","Engine","Ratchet, pawl","Jackhammer","Chainsaw","Vehicle","Light engine (high frequency)"]
    if float(onsetpred) <= float(classThreshold):
        print("low onset pred",float(onsetpred)," ", float(classThreshold))
        return 3
    for i in range(len(ambient)):
        if onsetclass == ambient[i]:
            return 0
    for i in range(len(anomaly)):
        if onsetclass == anomaly[i]:
            return 1
    print("detectanomaly function last return statement")
    return 2
#sampling rate is variable

#filename="rec_2023-06-10T14-37-00.wav"
# recDuration="20"
# recSamplingRate="48000"
# recFormat="wav"

while 1:
    ############### Load Data ################
    f = open("/home/raspberry/cloud_client/config_files/device.json")
    data = json.load(f)
    deviceId=data["deviceId"]
    deviceType=data["deviceType"]
    f= open("/home/raspberry/cloud_client/config_files/sound.json")
    data = json.load(f)
    recDuration=data["recDuration"]
    recFormat=data["recFormat"]
    recSamplingRate=data["recSamplingRate"]
    threshold=data["onsetThreshold"]
    classThreshold=data["classThreshold"]
    f= open("/tmp/gps.json")
    data = json.load(f)
    gpsLat=float(data["lat"])
    gpsLong=float(data["long"])
    ############### Load Data ################

    flag, dir_list=filecheck()
    #logic for waiting until new files are generated
    if flag==False:
        print("No files... Sleeping...")
        time.sleep(30)
    else:
        #dir_list=filecheck()
        for file in dir_list:
            # Load audio file
            audio_file = file
            y_init, sr_init = librosa.load(path2+audio_file,sr=16000)
            print("File found! path is ",path2+file," sr is ",sr_init)
            print("type of y_init is ",(y_init.dtype)," size is",len(y_init))
            if len(y_init)<15600:
                break
            #print("y is",y_init)
            # Plot waveform of amplitude vs time
            #plt.figure(figsize=(14, 5))
            #fig, ax = plt.subplots(nrows=3, sharex=True)

            # librosa.display.waveshow(y_init, sr=sr_init, ax=ax[0])
            # ax[0].set(title='Envelope view, mono')
            # ax[0].label_outer()

            # plt.plot(y_init,x)
            #plt.show()

            # Set loudness threshold
            # threshold = 0.005

            # Find timestamps when the sound goes over the threshold
            onset_frames = librosa.onset.onset_detect(y=y_init, sr=sr_init)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr_init)
            
            #print(y_init.shape)
            #print("onset times are ",onset_times,type(onset_times))
            onset_detects=[]
            onset_detects_values=[]
            #onset_y_init=[]
            onset_classes=[]
            onset_detects_anomaly=[]
            onset_detects_values_anomaly=[]
            onset_classes_anomaly=[]
            onset_detects_unknown=[]
            onset_detects_values_unknown=[]
            onset_classes_unknown=[]
            
            onset_classes_dict={"className":"","onsetTime":"","onsetMagnitude":"","confidence":""}
            # Print timestamps when the sound goes over the threshold
            for i in range(len(onset_times)):
                if int(onset_times[i] * sr_init) < len(y_init) and y_init[int(onset_times[i] * sr_init)] > threshold:
                    #print(onset_time)
                    #onset_detects.append(str(onset_times[i]))
                    #onset_detects_values.append(str(y_init[int(onset_times[i] * sr_init)]))
                    
                    onset=int(onset_times[i] * sr_init)
                    
                    onset_classes_dict["onsetTime"]=str(onset_times[i])
                    onset_classes_dict["onsetMagnitude"]=str(y_init[int(onset_times[i] * sr_init)])
                    #onset_y_init.append(onset)
                    if (onset-7800)>0 and ((onset+10800)<len(y_init)):
                        temp_data = y_init[onset-4800:onset+10800]
                    elif (onset+10800)>=len(y_init):
                        temp_data = y_init[(len(y_init)-15600):len(y_init)]
                    else:
                        temp_data = y_init[0:15600]
                    filename=path2+str(file)+str(onset)
                    # librosa.output.write_wav(filename,temp_data,sr_init,norm=False)
                    onsetclass,onsetpred=inference(temp_data,filename)
                    onset_classes_dict["className"]=onsetclass
                    onset_classes_dict["confidence"]=onsetpred
                    
                    flag=detectanomaly(onsetclass,onsetpred,classThreshold)
                    print("flag is ",flag)
                    
                    if flag==0:
                        onset_classes.append(onset_classes_dict)
                    if flag==1:
                        #onset_detects_anomaly.append(str(onset_times[i]))
                        #onset_detects_values_anomaly.append(str(y_init[int(onset_times[i] * sr_init)]))
                        onset_classes_anomaly.append(onset_classes_dict)
                    if flag==2:
                        #onset_detects_unknown.append(str(onset_times[i]))
                        #onset_detects_values_unknown.append(str(y_init[int(onset_times[i] * sr_init)]))
                        onset_classes_unknown.append(onset_classes_dict)

            #print("detected time are",onset_detects)
            #print("detected values are",onset_detects_values)
            print("detected classes are",onset_classes)
            #if len(onset_detects) > 0:
            if len(onset_classes)!=0:
                build_payload(onset_classes,file)
            if len(onset_classes_anomaly)!=0:
                build_anomaly_payload(onset_classes_anomaly,file)
            if len(onset_classes_unknown)!=0:
                build_unknown_payload(onset_classes_unknown,file)
            os.rename(path2+audio_file,path3+audio_file)
                
            #print("detected y_init times are",onset_y_init)

            # for onset in onset_y_init:
            #     if (onset-7800)>0:
            #         temp_data = y_init[onset-4800:onset+10800]
            #     elif (onset+7800)>=len(y_init):
            #         temp_data = y_init[(len(y_init)-15600):len(y_init)]
            #     else:
            #         temp_data = y_init[0:15600]
            #     filename=path2+str(file)+str(onset)
            #     #librosa.output.write_wav(filename,temp_data,sr_init,norm=False)
            #     onsetclass,onsetpred=inference(temp_data,filename)
            #     onset_classes.append({onsetclass:onsetpred})
            #     if classes.detectanomaly(onsetclass)==1:
            #         onset_classes_anomaly.append({onsetclass:onsetpred})
            #     if classes.detectanomaly(onsetclass)==2:
            #         onset_classes_unknown.append({onsetclass:onsetpred})


                
            #build_payload(onset_detects,onset_detects_values,onset_classes,file)
            #os.remove(path2+audio_file)
            #os.rename(path2+audio_file,path3+audio_file)
    #break
        
