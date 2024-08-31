if (canListen) {
    let buttonDown = (digitalIn(listenButton) == 1);
    if (buttonDown && !listening) {
        listening = true;
        startRecording();
    }
    if (!buttonDown && listening) {
        listening = false;
        stopRecording();
        sendScreenie();
    }
}

if (speaking) {
    moveJaw();
    await mSec(1000);
}

await mSec(10);