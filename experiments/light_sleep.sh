#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils

avahi-publish-service "Embodied" _embodied._tcp 5020 &