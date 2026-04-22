#!/bin/bash

Xvfb :99 -screen 0 1280x1024x24 -ac &
export DISPLAY=:99

sleep 1

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
