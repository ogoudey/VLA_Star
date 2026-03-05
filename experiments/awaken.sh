#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils

while true; do
    NAME=$(avahi-browse -rt _myhelper._tcp | grep "username=" | awk -F'=' '{print $2}')
    EMBODIED_VLA_STAR=$(avahi-browse -rt _embodied._tcp | grep address | awk -F'[][]' '{print $2}')
    if [ -n "$EMBODIED_VLA_STAR" ]; then
        echo "Found embodied VLA* at $NAME@$EMBODIED_VLA_STAR"
        break
    fi
    sleep 1
done

echo "======================================"
echo "Awakening..."
echo "======================================"
echo ""



ssh "$NAME@$EMBODIED_VLA_STAR" "./VLA_Star/experiments/run_embodied.sh"