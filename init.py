import os
import subprocess

from google import genai
from google.genai import types
import subprocess
import sys

import subprocess

# access GEMINI_API_KEY from environment variables
geminiKey = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=geminiKey)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="""You are a program for generating Arduino codes to operate step motors connected to the board. 
        You are given a task description and a list of requirements. 
        You need to generate Arduino C++ code that complete one instruction at a time.
        You need to generate Arduino C++ code that complete one instruction at a time.
        Some pin definition are given in the following code:
        ``` C++
        #define X_STEP_PIN         54
        #define X_DIR_PIN          55
        #define X_ENABLE_PIN       38
        ```
        Please generate a code for the following task: 
        """),
    contents="Rotate the motor 360 degrees",
)

# strip C++ code from response
code = response.text.split("``` C++\n")[1].split("\n```")[0]

with open("build/code.cpp", "w") as f:
    f.write(code)

sketch_path = "build/iForgeHackathonBestGroup.ino"  # Change this to your .ino file
port = "COM3"  # Change this if your Arduino is on a different port
fqbn = "arduino:avr:mega"  # Replace with the correct FQBN for your board

compile_command = [
    'arduino-cli',
    'compile',
    '--fqbn',
    fqbn,
    sketch_path
]
compile_process = subprocess.run(compile_command, capture_output=True, text=True, check=True)

upload_command = [
    'arduino-cli',
    'upload',
    '--fqbn',
    fqbn,
    '--port',
    port,
    sketch_path
]

try:
    print(f"Attempting to upload '{sketch_path}' to port '{port}' with FQBN '{fqbn}'...")
    process = subprocess.run(upload_command, capture_output=True, text=True, check=True)
    print("Successfully uploaded the sketch!")
    print("Standard Output:")
    print(process.stdout)
    print("Standard Error:")
    print(process.stderr)

except subprocess.CalledProcessError as e:
    print(f"Error during upload:")
    print("Return Code:", e.returncode)
    print("Standard Output:", e.stdout)
    print("Standard Error:", e.stderr)

