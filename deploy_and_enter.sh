#!/bin/bash

docker build -t pc_configurator .

docker rm -f pc_configurator 2>/dev/null || true

docker run -d \
  --name pc_configurator \
  -p 8000:8000 \
  -v "$(pwd)/data:/usr/src/app/data" \
  -e SQLITE_PATH=/usr/src/app/data/db.sqlite3 \
  --shm-size=2gb \
  pc_configurator

sleep 2

docker exec -it pc_configurator bash -c "export DISPLAY=:99 && exec bash"