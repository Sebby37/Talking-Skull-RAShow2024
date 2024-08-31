import openai
import requests
from fastapi import FastAPI, UploadFile

# OpenAI client
client = openai.OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="No-bone-y knows!"
)

# Audio transcription
def transcribe_audio(audio: bytes) -> str:
    open("userSpeech.wav", "wb").write(audio)
    
    r = requests.post("http://localhost:8079/inference", data={
        "temperature": 0.0,
        "temperature_inc": 0.2,
        "response_format": "json"
    }, files={"file": open("userSpeech.wav", "rb")})
    
    transcription = r.json()["text"].strip()
    print("Got audio transcription:", transcription)
    return transcription

# Image captioning
def caption_img(img: str) -> str:
    open("userImg.png", "wb").write(img)
    
    r = requests.post("http://localhost:8081/caption", files={
        "img": open("userImg.png", "rb")
    })
    
    caption = r.json()["caption"]
    print("Got image caption:", caption)
    return caption

# LLM generation
def generate_response(speech: str, img_caption: str) -> str:
    # Setup prompts
    system_prompt = open("system_prompt.txt").read()
    user_message = f'''{system_prompt}\n<VISION>{img_caption}</VISION>\n{speech}'''
    messages = [ # Google, why in hell did you not include a system prompt with your Gemma models?
            {
                "role": "user",
                "content": user_message
            }
        ]
    
    print("System Prompt:", system_prompt, "\n")
    print("User Message: ", user_message, "\n")
    
    try:
        completion = client.chat.completions.create(
            model="T-9000", # Get it????
            messages=messages
        )
    except Exception as e:
        return {
            "content": "Something went wrong, I can feel it in my bones!",
            "error": e
        }
    
    print(completion.dict())
    
    return {
        "content": completion.choices[0].message.content.strip(),
        "error": None
    }

# Route
app = FastAPI()
@app.post("/doTheThing")
async def do_the_thing(audio: UploadFile, img: UploadFile):
    # Convert audio + img to text
    speech = transcribe_audio(await audio.read())
    img_caption = caption_img(await img.read())
    
    # Generate response
    return generate_response(speech, img_caption)
