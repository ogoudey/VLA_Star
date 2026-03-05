#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils

INSTANCE_NAME="Embodied"
SERVICE_TYPE="_embodied._tcp"
PORT=5020

PID=$(pgrep -f "avahi-publish-service $INSTANCE_NAME $SERVICE_TYPE $PORT")

if [ -n "$PID" ]; then
    echo "Stopping existing Avahi publisher (PID $PID)"
    kill "$PID"
    sleep 1  # give it a moment to clean up
fi

avahi-publish-service $INSTANCE_NAME $SERVICE_TYPE $PORT username=$USER &  # NOT a "USERNAME"
sleep 1