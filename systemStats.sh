#!/bin/bash

# Function to get CPU usage percentage
get_cpu_usage() {
  cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
  
  # Add sign to the CPU usage percentage
  if (( $(echo "$cpu_usage >= 0" | bc -l) )); then
    cpu_usage="+$cpu_usage"
  fi
  
  echo "$cpu_usage%"
}

# Function to get RAM usage percentage
get_ram_usage() {
  ram_usage=$(free -m | awk '/Mem/{printf "%.2f%%", ($3/$2) * 100}')
  echo "$ram_usage"
}

# Function to get CPU temperature in Celsius
get_cpu_temperature() {
  cpu_temp=$(vcgencmd measure_temp | cut -d= -f2 | cut -d"'" -f1)
  echo "$cpu_temp"
}

# Function to get disk usage percentage
get_disk_usage() {
  disk_usage=$(df -h / | awk 'NR==2 {print $5}')
  echo "$disk_usage"
}

# Function to get system uptime
get_system_uptime() {
  uptime=$(uptime -p)
  echo "$uptime"
}

# Loop to continuously write data to JSON file
while true; do
  cpu=$(get_cpu_usage)
  ram=$(get_ram_usage)
  temp=$(get_cpu_temperature)
  disk=$(get_disk_usage)
  uptime=$(get_system_uptime)

  # Create JSON object
  json="{\"cpu_usage\": \"$cpu\", \"ram_usage\": \"$ram\", \"cpu_temperature\": \"$temp\", \"disk_usage\": \"$disk\", \"uptime\": \"$uptime\"}"

  # Write JSON object to temporary file
  echo "$json" > /tmp/system_stats.json

  # Delay for 1 second before updating again
  sleep 1
done
