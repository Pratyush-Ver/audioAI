#!/bin/bash

# Check if the file path argument is provided
if [ -z "$1" ]; then
  echo "Error: File path argument is missing."
  echo "Usage: $0 <file_path> <json_file>"
  exit 1
fi

# Assign the file path argument
file_path="$1"

# Assign the JSON file argument
json_file="/home/ubuntu/rasp_test/checksumMap/checkSumMap.json"

file_name=$(basename "$file_path")
# Read the expected checksum from the JSON file
# expected_checksum=$(jq -r '.remote.checkSum' "$json_file")

# Calculate the checksum of the file
checksum=$(md5sum "$file_path" | awk '{print $1}')

jq --arg variable "$file_name" '.remote.variable = $variable' "$json_file"

jq --arg variable "$timestamp" '.remote.timeStamp = $variable' "$json_file"

jq --arg variable "$revision" '.remote.revision = $variable' "$json_file"

# Compare the calculated checksum with the expected checksum
# if [[ "$checksum" == "$expected_checksum" ]]; then
#   echo "Checksum verification successful!"
#   exit 0  # Exit with success status
# else
#   echo "Checksum verification failed!"
#   exit 1  # Exit with fail status
# fi
