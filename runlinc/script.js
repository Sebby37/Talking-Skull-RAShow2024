// Skull Stuff
let canListen = true;
let listening = false;
let speaking = false;
let jawClosed = false;

class SkullStates {
    static WAITING = "Sleeping";
    static LISTENING = "Listening";
    static THINKING = "Thinking";
    static SPEAKING = "Speaking";
}

// Webcam stuff
const WIDTH = 320;
let height = 0; // Computed based on input stream
let streaming = false
let webcam = null;

// Websocket stuff
let socket = null
class BoneCodes {
    // Basically stuff the client sends
    static START_RECORDING = "START_RECORDING";
    static STOP_RECORDING = "STOP_RECORDING";
    static SCREENIE = "SCREENIE";
    
    // Stuff server sends
    static GENERATION_BEGIN = "GENERATION_BEGIN";
    static GENERATION_COMPLETE = "GENERATION_COMPLETE";
    static SPEAKING_END = "SPEAKING_END";
}
let prevCommand = null;

function setupVideo() {
    webcam = document.getElementById("webcam");
    
    navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
            webcam.srcObject = stream;
            webcam.play();
        })
        .catch((err) => {
            console.error("Failed to start stream: " + err)
        });
    
    webcam.addEventListener("canplay", (event) => {
        if (streaming)
            return;
        
        height = webcam.videoHeight / (webcam.videoWidth / WIDTH);
        if (isNaN(height))
            height = width / (4 / 3);
        
        webcam.setAttribute("width", WIDTH)
        webcam.setAttribute("height", height)
        
        streaming = true;
    }, false);
}

function takePicture() {
    if (!streaming)
        return null;
    
    let canvas = document.createElement("canvas");
    canvas.width = WIDTH;
    canvas.height = height;
    
    let ctx = canvas.getContext("2d");
    ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    
    return canvas.toDataURL("image/png")
}

function setupWebsocket() {
    socket = new WebSocket("ws://192.168.98.185:8765");
    
    socket.addEventListener("open", (event) => {
        console.log("Websocket opened!", event);
        socket.send("Smello!");
    });
    
    socket.addEventListener("message", (event) => {
        console.log("Message from server:", event.data, event);
        handleMessage(event.data);
    });
}

function handleMessage(message) {
    switch (message.split(" ")[0]) {
        case BoneCodes.GENERATION_BEGIN:
            {
                console.log("Generation has begun...");
                generationBegun();
                break;
            }
        case BoneCodes.GENERATION_COMPLETE:
            {
                console.log("Generation complete! Got message:", message);
                generationComplete(message.slice(BoneCodes.GENERATION_COMPLETE.length + 1));
                break;
            }
        case BoneCodes.SPEAKING_END:
            {
                console.log("Speaking has ended!");
                speakEnd();
                break;
            }
    }
}

function startRecording() {
    if (socket == null)
        return;
    
    prevCommand = BoneCodes.START_RECORDING;
    socket.send(BoneCodes.START_RECORDING);
    setSkullState(SkullStates.LISTENING);
    document.getElementById("response").innerText = "...";
}

function stopRecording() {
    if (socket == null)
        return;
    
    prevCommand = BoneCodes.STOP_RECORDING;
    socket.send(BoneCodes.STOP_RECORDING);
}

function sendScreenie() {
    if (socket == null)
        return;
    
    let screenie = takePicture();
    
    prevCommand = BoneCodes.SCREENIE;
    socket.send(BoneCodes.SCREENIE + " " + screenie);
}

function generationBegun() {
    // To be implemented moreso in runlinc
    // But mainly frontend stuff I'd say
    canListen = false;
    setSkullState(SkullStates.THINKING);
}

function generationComplete(message) {
    speaking = true;
    setSkullState(SkullStates.SPEAKING);
    document.getElementById("response").innerText = JSON.parse(message).content;
}

function speakEnd() {
    // Yet-again, a runlinc function moreso
    // NOTE: servo value must be between 0 and 60, otherwise it flips itself off the skull lmao
    speaking = false;
    canListen = true;
    setSkullState(SkullStates.WAITING);
}

function moveJaw() {
    jawClosed = !jawClosed;
    setServo(mouthServo, jawClosed ? 60 : 0);
}

function setSkullState(newState) {
    // Set image
    let skullImg = document.getElementById("skullImg");
    skullImg.src = `https://raw.githubusercontent.com/Sebby37/Talking-Skull-RAShow2024/main/Media/skull-${newState.toLowerCase()}.jpeg`
    
    // Set text
    document.getElementById("skullState").innerText = newState;
}

function loadSkullDecos() {
    const skulls = ["aniskull_Flee.gif",
        "arroba.gif",
        "nurp-skullw.gif",
        "skullcol.gif",
        "skull_enter.gif",
        "skull_flag.gif",
        "skullflame.gif",
        "skull.gif",
        "skullspin.gif",
        "spinningskull.gif"
    ];
    
    let skullDecos = document.getElementsByClassName("skullDeco");
    for (const img of skullDecos) {
        let chosenSkull = skulls[Math.floor(Math.random() * skulls.length)];
        img.src = null; // Do this once I've pushed
    }
}

setupVideo();
setupWebsocket();
setSkullState(SkullStates.WAITING);