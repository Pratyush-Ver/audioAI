#!/bin/bash

# Get GPS location data
activate_gps() {
echo -e "AT+QGPS=1" > /dev/ttyUSB2
sleep 180
}
write_gps(){
gps=$(sudo mmcli -m 0 --location-get)

# Extract latitude and longitude values
latitude=$(echo "$gps" | grep -oP '(?<=latitude: )[^ ]+')
longitude=$(echo "$gps" | grep -oP '(?<=longitude: )[^ ]+')

# Print values
echo "Latitude: $latitude"
echo "Longitude: $longitude"
echo "{\"lat\": \"$latitude\", \"long\": \"$longitude\"}" > /tmp/gps.json
}

activate_gps

while true; do
  write_gps
  sleep 60
done
