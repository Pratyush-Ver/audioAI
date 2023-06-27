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
 
path = "/home/raspberry/rec2"
path2 = "/home/raspberry/rec2/"

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
"peakTimeStamp":[],
"peakMagnitude":[]
}

def build_payload(onset_detects,onset_detects_values,filename):
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%YT%H-%M-%S")
    payload["timeStamp"]=dt_string
    payload["recFileName"]=filename
    payload["recTimeStamp"]=filename.split("_")[1]
    payload["recDuration"]=recDuration
    payload["recSamplingRate"]=recSamplingRate
    payload["recFormat"]=recFormat
    payload["detectionCount"]=len(onset_detects)
    payload["onsetThreshold"]=threshold
    payload["peakTimeStamp"]=onset_detects
    payload["peakMagnitude"]=onset_detects_values
    json_write(payload)

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
    yamnet_classes = class_names('yamnet_class_map.csv')
    #interpreter = tf.lite.Interpreter(model_path="yamnet.tflite")
    interpreter = tf.Interpreter(model_path="yamnet.tflite")
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    interpreter.set_tensor(inputs[0]['index'], np.expand_dims(temp_data, axis=0))
    interpreter.invoke()
    scores = interpreter.get_tensor(outputs[0]['index'])
    prediction = np.mean(scores, axis=0)
    top5_i = np.argsort(prediction)[::-1][:5]
    print(filename, ':\n' + 
          '\n'.join('  {:12s}: {:.3f}'.format(yamnet_classes[i], prediction[i])
                    for i in top5_i))

#sampling rate is variable

#filename="rec_2023-06-10T14-37-00.wav"
recDuration="20"
recSamplingRate="48000"
recFormat="wav"

while 1:
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
            threshold = 0.01

            # Find timestamps when the sound goes over the threshold
            onset_frames = librosa.onset.onset_detect(y=y_init, sr=sr_init)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr_init)
            #print(y_init.shape)
            #print("onset times are ",onset_times,type(onset_times))
            onset_detects=[]
            onset_detects_values=[]
            onset_y_init=[]
            # Print timestamps when the sound goes over the threshold
            for onset_time in onset_times:
                if int(onset_time * sr_init) < len(y_init) and y_init[int(onset_time * sr_init)] > threshold:
                    #print(onset_time)
                    onset_detects.append(str(onset_time))
                    onset_detects_values.append(str(y_init[int(onset_time * sr_init)]))
                    onset_y_init.append(int(onset_time * sr_init))
            print("detected time are",onset_detects)
            print("detected values are",onset_detects_values)
            print("detected y_init times are",onset_y_init)
            for onset in onset_y_init:
                if (onset-7800)>0:
                    temp_data = y_init[onset-7800:onset+7800]
                else:
                    temp_data = y_init[0:15600]
                filename=path2+str(file)+str(onset)
                #librosa.output.write_wav(filename,temp_data,sr_init,norm=False)
                inference(temp_data,filename)


                
            #build_payload(onset_detects,onset_detects_values,file)
            #os.remove(path2+audio_file)
    break
        