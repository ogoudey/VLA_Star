#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils

avahi-publish-service "HelperNode" _myhelper._tcp 5000 &