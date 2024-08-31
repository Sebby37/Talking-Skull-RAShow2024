#!/bin/bash
cd ../models/llm
#./llama-server -m Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf -c 512 -t 8 --host 0.0.0.0 --port 8080
./llama-server -m gemma-2-2b-it-Q4_K_M.gguf -c 512 -t 8 --host 0.0.0.0 --port 8080
cd ../../servers
