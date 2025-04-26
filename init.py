import os
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
        You need to generate C++ code that complete one instruction at a time.
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