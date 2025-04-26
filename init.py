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
        system_instruction="""You need to generate Arduino code that is ready to compile for the given instruction. ONLY GENERATE CODE.
        Some pin definition are given in the following code:
        X_STEP_PIN         54
        X_DIR_PIN          55
        X_ENABLE_PIN       38
        Please generate a code for the following task: 
        """),
    contents="Rotate the motor 360 degrees, and then FULL STOP",
)
# strip C++ code from response
def extract_code_from_response(response):
    code_blocks = []
    in_code_block = False
    current_code = ""
    for line in response.text.splitlines():
        if line.startswith("```"):
            if in_code_block:
                code_blocks.append(current_code.strip())
                current_code = ""
                in_code_block = False
            else:
                in_code_block = True
        elif in_code_block:
            current_code += line + "\n"
    return code_blocks

# Example usage (assuming 'response' is your Gemini API response object)
code_blocks = extract_code_from_response(response)  # Changed 'code' to 'code_blocks'
if code_blocks:  # Check if the list is not empty
    code = code_blocks[0]  # Get the first code block
    print("Writing first code block to .ino")
    with open("build/build.ino", "w") as f:
        f.write(code)
else:
    print("No code blocks found in the response.")
    # Handle the case where no code is found, e.g., write an empty file or raise an error
    with open("build/build.ino", "w") as f:
        f.write("") # Write an empty string

sketch_path = "build/build.ino"  # Change this to your .ino file
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

