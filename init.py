import os
import subprocess

from google import genai
from google.genai import types

# access GEMINI_API_KEY from environment variables
geminiKey = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=geminiKey)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction="""You are a program for generating Arduino codes to operate step motors connected to the board. 
        You are given a task description and a list of requirements. 
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

print(code)

# prompt the console to compile and upload the code to the Arduino board. press Y to proceed, N to cancel
confirm = input("Do you conform to compile and upload the code to the Arduino board? (Y/N) ")
if confirm == "Y":
    # compile and upload the code to the Arduino board in this process
    compile_process = subprocess.run(["arduino-cli", "compile", "--board", "arduino:avr:uno", "--port", "/dev/ttyACM0", "--verbose", "build/code.ino"])
    if compile_process.returncode == 0:
        upload_process = subprocess.run(
            ["arduino-cli", "upload", "--board", "arduino:avr:uno", "--port", "/dev/ttyACM0", "--verbose", "build/code.ino"])
    else:
        print("Compile failed")
else:
    print("Cancelled")