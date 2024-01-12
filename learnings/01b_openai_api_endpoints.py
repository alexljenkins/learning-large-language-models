"""
Checking out all the different models and data types of the OpenAI API.
https://platform.openai.com/docs/models
"""
from dotenv import load_dotenv
load_dotenv()

import openai
import webbrowser

def print_all_models():
    
    models = openai.Model.list()
    print(models.data[0].root)
    print(mod.root for mod in models.data)

def basic_text_completion():
    completion = openai.Completion.create(model="ada", prompt="Bill Gates is a", max_tokens=100, temperature=0.9)
    print(completion.choices[0].text)


def basic_img_gen():
    image_gen = openai.Image.create(prompt="lifelike picture of a basketball", n=2, size="512x512")
    # img1 = image_gen.data[0].url
    for img in image_gen.data:
        webbrowser.open_new_tab(img.url)

def basic_transcribe(audio_filepath):
    audio = open(audio_filepath, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio)
    print(transcript)
    return transcript
