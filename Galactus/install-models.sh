#!/bin/bash

#
# Ok, so this script simply downloads the models and their servers, but does NOT handle requirements
# As for requirements here, you'll need git, git-lfs, wget, build-essentials (make, g++), and all the modules
# inside florence-server.py and Florence-2-base.
# These are all being run on the CPU at the moment btw, I installed torch with the following command (thanks claude):
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
#

cd models

# First of all we install Florence and such
echo "Installing Florence-2"
cd img
git clone https://huggingface.co/microsoft/Florence-2-base
cd ..

# Next we install llama.cpp's server and the llm
# I've opted for llama 3.1 8b, as I've had good luck with llama 3 8b in the past
# Edit: Well I originally opted for L3.1, but it was so dang slow I jumped ship to Gemma 2 2b, seems to be working pretty well aside from the lack of system prompt support
echo "Installing Llama.cpp + Gemma-2-2b-it"
cd llm
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make GGML_OPENBLAS=1 -j24 llama-server
cp llama-server ..
cd ..
rm -rf llama.cpp
wget "https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/resolve/main/gemma-2-2b-it-Q4_K_M.gguf"
cd ..

# Now we install whisper.cpp's server and it's model
# I'm currently opting for whisper tiny en for its teensy memory footprint, but large v2 is super good and might work better
echo "Installing Whisper.cpp + Whisper Tiny"
cd stt
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make GGML_OPENBLAS=1 -j24 server
cp server ../whisper-server
cd ..
rm -rf whisper.cpp
wget "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
cd ..

cd ..
