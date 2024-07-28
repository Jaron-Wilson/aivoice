"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python


MAKE KEY AVAILABLE
export GEMINI_API_KEY=KEY
"""

import os
import pyaudio
import keyboard
import wave

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def record_audio():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000  # orig = 16000
    CHUNK = 1024
    audio = pyaudio.PyAudio()

    print(f"Start speaking... (Press 'Enter' to stop)")
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed('enter'):
            print(f"Stopping recording.")
            break

    stream.stop_stream()
    stream.close()

    wf = wave.open("temp_audio.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return "temp_audio.wav"


print("Recording File:" + record_audio())


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

# TODO Make these files available on the local file system
# You may need to update the file paths
file = upload_to_gemini("temp_audio.wav", mime_type="audio/wav")

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                file,
                "convert this into text, if you hear nothing output (NONE)",
            ],
        },
    ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

if response.text in "NONE":
    print("\n\nI hear nothing!: \n" + response.text)
else:
    responseAnswer = chat_session.send_message("Answer to your best ability: " + response.text)

    genai.delete_file(file.name)
    print(f'Deleted from GEMINI {file.display_name}.')
    print("\n\nSpeech to text looks like this: \n" + response.text)
    print("\n\nAnswer to your question is this:\n" + responseAnswer.text)
