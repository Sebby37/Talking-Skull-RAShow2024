import requests
from fastapi import FastAPI, UploadFile

# Audio transcription
def transcribe_audio(audio: bytes) -> str:
    open("userSpeech.wav", "wb").write(audio)
    
    r = requests.post("http://localhost:8079/inference", data={
        "temperature": 0.0,
        "temperature_inc": 0.2,
        "response_format": "json"
    }, files={"file": open("userSpeech.wav", "rb")})
    
    transcription = r.json()["text"].strip()
    print("Got speech transcription:", transcription)
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
    user_message = f'''<VISION>{img_caption}</VISION>\n{speech}'''
    
    print(system_prompt, "\n")
    print(user_message, "\n")
    
    import json
    print(json.dumps({
        "model": "T-9000", # Get it????
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }))
    
    # TODO: Somethings muffing up here, the JSON isn't properly being decoded server-side or smth idk
    # EDIT: I tried it with openai, I think the generation speed is like WAYYYYY too slow or smth
    r = requests.post("http://localhost:8080/v1/chat/completions", data={
        "model": "T-9000", # Get it????
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    })
    
    if r.status_code != 200:
        print("Failed to generate response:", r.text, r.status_code)
        return {
            "content": "Something went wrong, I can feel it in my bones!",
            "error": str(r)
        }
    
    return {
        "content": r.json()["choices"][0]["message"]["content"].strip(),
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
