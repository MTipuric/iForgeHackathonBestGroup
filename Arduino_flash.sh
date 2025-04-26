#!/bin/bash
# This script compiles and uploads an Arduino sketch using arduino-cli.

# Set the Arduino sketch file path
sketch_path="./A_run.ino" # Change this to your .ino file

# Set the port
port="COM3" # Change this if your Arduino is on a different port

# Perform the upload
echo "Uploading sketch '$sketch_path' to board on port '$port' with FQBN '$fqbn'..."
arduino-cli upload --fqbn "$fqbn" --port "$port" "$sketch_path"

# Check the result of the upload
if [ $? -eq 0 ]; then
  echo "Successfully uploaded the sketch!"
else
  echo "Error uploading the sketch.  Please check the FQBN, port, and connections."
  exit 1
fi
