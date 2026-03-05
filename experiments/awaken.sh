#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

echo "Installing apt packages"
sudo apt install avahi-utils


SERVICE="_embodied._tcp"



while true; do
    FOUND=$(avahi-browse -rt "$SERVICE" 2>/dev/null | awk '
        /hostname = \[/ {
            line = $0
            sub(/.*\[/,"",line)
            sub(/\].*/,"",line)
            hostname=line
        }
        /txt = \[.*username=/ {
            line = $0
            sub(/.*username=/,"",line)
            sub(/"].*/,"",line)
            username=line
        }
        hostname && username { print username " " hostname; exit }
    ')

    if [ -n "$FOUND" ]; then
        NAME=$(echo "$FOUND" | awk '{print $1}')
        EMBODIED_VLA_STAR=$(echo "$FOUND" | awk '{print $2}')
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