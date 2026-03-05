#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils

while true; do
    EMBODIED_VLA_STAR=$(avahi-browse -rt _emvodied._tcp | grep address | awk -F'[][]' '{print $2}')
    if [ -n "$EMBODIED_VLA_STAR" ]; then
        echo "Found embodied VLA* at $EMBODIED_VLA_STAR"
        break
    fi
    sleep 1
done

echo "======================================"
echo "Awakening..."
echo "======================================"
echo ""



ssh "$1" "./VLA_Star/experiments/run_embodied.sh"