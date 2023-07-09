#!/bin/sh

card=`arecord -l | grep card | awk '{print $2}' | sed 's/://g'`
device=`arecord -l | grep card | awk '{print $8}' | sed 's/://g'`
echo "$card"
echo "$device"
#duration=20
mic=0

json=$(cat /home/raspberry/cloud_client/config_files/sound.json)

duration=$(echo $json | jq -r '.recDuration')
format=$(echo $json | jq -r '.recFormat')
samplingrate=$(echo $json | jq -r '.recSamplingRate')


stamp() {
    TEXT="rec"
    DATE=`date +%d-%m-%Y`
    TIME=`date +%H-%M-%S`
    #ZONE=`date +"%Z %z"`
    echo ${TEXT}_${DATE}T${TIME}
}


miccheck() {
    card=`arecord -l | grep card | awk '{print $2}' | sed 's/://g'`
    device=`arecord -l | grep card | awk '{print $8}' | sed 's/://g'`
    if [ -z "$card" ]
        then
        echo "No mic detected"
        mic=0
        exit 1
        # execute command here
    else
        echo "Mic detected!"
        mic=1
    fi
}
miccheck
while [ $mic -eq 1 ]
do
    miccheck
    filename=`stamp`
    arecord -D hw:$card,$device -d $duration -f S16_LE -r $samplingrate -t $format -c 1 /tmp/$filename.$format
    cp /tmp/$filename.$format /home/raspberry/rec/$filename.$format
    cp /home/raspberry/rec/$filename.$format /home/raspberry/recTest/testRecord.$format
    sleep 0.5
done
