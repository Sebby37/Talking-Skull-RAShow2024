import asyncio
import threading
from typing import Union
import numpy as np
import pyaudio
import pyttsx3
import requests
import scipy.io.wavfile as wav
from websockets.asyncio.server import serve

GALACTUS_ROUTE = "http://0.0.0.0:8315/doTheThing"

# Response codes and such
class BoneCodes:
    # Basically stuff the client sends
    START_RECORDING = "START_RECORDING"
    STOP_RECORDING = "STOP_RECORDING"
    SCREENIE = "SCREENIE"
    
    # Stuff server sends
    GENERATION_BEGIN = "GENERATION_BEGIN"
    GENERATION_COMPLETE = "GENERATION_COMPLETE"
    SPEAKING_END = "SPEAKING_END"
    
# Some statics, unfortunately this can only really serve one client at a time, oh well!
has_audio, has_screenie = False, False
recording = False
screenie = None

# TTS (screw you window.speechSynthesis for not listing any voices)
engine = pyttsx3.init()

def record_thread():
    global recording, has_audio
    
    RATE = 16000
    CHUNKSIZE = 1024
    p = pyaudio.PyAudio()

    while True:
        if recording:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNKSIZE)
            frames = []

            while recording:
                data = stream.read(CHUNKSIZE)
                numpydata = np.frombuffer(data, dtype=np.int16) # The good stuff
                frames.append(numpydata)
            
            print("Done proper recording, n frames are:", len(frames))
            wav.write("transcription.wav", RATE, np.hstack(frames))
            stream.stop_stream()
            stream.close()
            has_audio = True

    p.terminate()

# Handles a client message
def handle_message(message: str) -> Union[str, None]:
    # Uhm yeah globals
    global recording, screenie, has_audio, has_screenie
    
    # Handle client codes
    match message.split()[0]:
        case BoneCodes.START_RECORDING:
            recording = True
        case BoneCodes.STOP_RECORDING:
            recording = False
            while not has_audio: pass # Wait for recording thread to finish (this probably isn't a good idea lol)
        case BoneCodes.SCREENIE:
            screenie = message[len(BoneCodes.SCREENIE) + 1:].split(",")[1]
            has_screenie = True
    
    # Begin generation here
    if has_audio and has_screenie:
        return BoneCodes.GENERATION_BEGIN

# Performs the actual text generation
def do_generation():
    open("screenie.png", "w+").write(screenie)
    r = requests.post(GALACTUS_ROUTE, files={"audio": open("transcription.wav", "rb"), "img": open("screenie.png", "rb")})
    return r.json()

def speak_generation(text: str):
    engine.say(text)
    engine.runAndWait()

# Handles a websocket connection
async def server(websocket):
    global recording, screenie, has_audio, has_screenie
    
    async for message in websocket:
        print("Got message:", message.strip() if len(message.strip()) < 500 else "[Large message, prolly a screenie]")
        res = handle_message(message.strip())
        
        # Running generation
        if res is BoneCodes.GENERATION_BEGIN:
            # Perform and send generation
            await websocket.send(BoneCodes.GENERATION_BEGIN)
            generation = do_generation()
            await websocket.send(BoneCodes.GENERATION_COMPLETE + " " + str(generation))
            speak_generation(generation["content"])
            await websocket.send(BoneCodes.SPEAKING_END)
            
            # Cleanup
            has_audio, has_screenie = False, False
            recording = False
            screenie = None
        # Sending whatever else message needs to be sent
        elif res is not None:
            await websocket.send(res)

async def main():
    record = threading.Thread(target=record_thread, daemon=True)
    record.start()
    async with serve(server, "0.0.0.0", 8765):
        await asyncio.get_running_loop().create_future() # Run forever!!!

if __name__ == "__main__":
    asyncio.run(main())