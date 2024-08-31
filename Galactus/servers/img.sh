#!/bin/bash
cd ../models/img
fastapi run florence-server.py --host 0.0.0.0 --port 8081
cd ../../servers