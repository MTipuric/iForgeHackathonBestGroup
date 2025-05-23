import ast
import os
import re
import subprocess

from google import genai
from google.genai import types
import subprocess
import sys
import ikpy
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import numpy as np
import time

"""
Inverse Kinematics
"""
def inverse_kinematics(start_degs, target_dist):
    left_arm_chain = Chain(name='robot_arm', links=[
        OriginLink(),
        URDFLink(
          name="BaseRotate",
          origin_translation=[0, 0, 0],
          origin_orientation=[0, 1.57, 0],
          rotation=[0, 0, 1],
        ),
        URDFLink(
          name="Shoulder_hinge",
          origin_translation=[0, 0, 0.4],
          origin_orientation=[0, 0, 0],
          rotation=[0, 1, 0],
        ),
        URDFLink(
          name="Elbow",
          origin_translation=[0, 0, 0.4],
          origin_orientation=[0, 0, 0],
          rotation=[0, 1, 0],
        ),
        URDFLink(
          name="End",
          origin_translation=[0, 0, 0],
          origin_orientation=[0, 0, 0],
          rotation=[0, 0, 0],
        )
    ])
    # initial_angles_degrees = [0, 0, 45, 45, 0]

    # Convert to radians
    initial_angles_radians = np.deg2rad(start_degs)

    # Get the initial forward kinematics
    initial_fk = left_arm_chain.forward_kinematics(initial_angles_radians)

    # Extract the initial end-effector position
    initial_end_effector_position = initial_fk[:3, 3]
    print(f"Initial end-effector position (x, y, z): {initial_end_effector_position}")

    # Define the target end-effector position (20 cm forward in X)
    # target_position = [0.2, 0, 0]
    target_joint_angles_radians = left_arm_chain.inverse_kinematics(target_dist)
    target_joint_angles_degrees = np.rad2deg(target_joint_angles_radians)

    print(f"Target joint angles (degrees): {target_joint_angles_degrees}")
    return target_joint_angles_degrees


"""
Gemini calls
"""

# access GEMINI_API_KEY from environment variables
geminiKey = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=geminiKey)

def generate_and_run(target_degrees):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You need to generate Arduino code that is ready to compile for the given instruction. ONLY GENERATE CODE.
            Some pin definition are given in the following code:
            ``` C++
            #define X_STEP_PIN         54
            #define X_DIR_PIN          55
            #define X_ENABLE_PIN       38
            #define Y_STEP_PIN         60
            #define Y_DIR_PIN          61
            #define Y_ENABLE_PIN       56

            #define Z_STEP_PIN         46
            #define Z_DIR_PIN          48
            #define Z_ENABLE_PIN       62
            ```
            Please generate a code for the following task: 
            """),
    contents=f"Rotate the X motor {target_degrees[1]}, and then FULL STOP. \
            Rotate the Y motor {target_degrees[2]}, and then FULL STOP. \
            Rotate the Z motor {target_degrees[3]}, and then FULL STOP"
)
    # strip C++ code from response
    code_start = r"```(.*?)\n"
    parts = re.split(code_start, response.text)
    code_blocks = parts[-1].split("```")[0]

    # Example usage (assuming 'response' is your Gemini API response object)
    if code_blocks:  # Check if the list is not empty
        print("Writing first code block to .ino")
        with open("build/build.ino", "w") as f:
            f.write(code_blocks)
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

def coordiate_generation(instruct):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="""I'm generating some coordinates in 3d space. 
            I'm using the following format: [x, y, z].
            please generate a series of 3d coordinates in Python lists forming the shape you are instructed to. 
            only printout the list.
                """),
        contents=instruct,
    )

    # strip C++ code from response
    code_start = r"```(.*?)\n"
    parts = re.split(code_start, response.text)
    code_blocks = parts[-1].split("```")[0]

    # parse list in the string to a list
    coord = ast.literal_eval(code_blocks)

    return coord

def main():

    instruction = input("Enter the instruction: ")
    coor = coordiate_generation(instruction)
    start = [0,0,45,45,0]

    for i in range(len(coor)):
        print(coor[i])
        target_angle = inverse_kinematics(start, coor[i])
        generate_and_run(target_angle)
        start = target_angle 

        time.sleep(10)

if __name__ == '__main__':
    main()