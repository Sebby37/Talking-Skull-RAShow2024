#!/bin/bash
cd ../models/stt
./whisper-server -m ggml-tiny.en.bin -t 8 --host 0.0.0.0 --port 8079
cd ../../servers