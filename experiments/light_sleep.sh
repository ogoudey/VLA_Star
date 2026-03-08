#!/usr/bin/env bash

# ==================================
#  Re-up the host's advertisements
# ==================================

echo "Installing apt packages"
sudo apt install avahi-utils

INSTANCE_NAME="$HOSTNAME" # like "embodied host", or "rpi", or something
SERVICE_TYPE="_bed._tcp"
PORT=5020

PID=$(pgrep -f "avahi-publish-service $INSTANCE_NAME $SERVICE_TYPE $PORT")

if [ -n "$PID" ]; then
    echo "Stopping existing Avahi publisher (PID $PID)"
    kill "$PID"
    sleep 1  # give it a moment to clean up
fi

avahi-publish-service $INSTANCE_NAME $SERVICE_TYPE $PORT username=$USER &  # NOT a "USERNAME"

aplay VLA_Star/experiments/boot.wav
sleep 1
