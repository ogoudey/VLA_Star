#!/usr/bin/env bash

# =====================================
#         Solely an interface 
# =====================================

# =====================================
#        Some platform detection 
# =====================================

OS_TYPE=$(uname -s)
if [ -f "/data/data/com.termux/files/usr/bin/termux-info" ]; then
    ENVIRONMENT="termux"
else
    ENVIRONMENT="linux"
fi
if command -v apt >/dev/null; then
    PACKAGE_MANAGER="apt"
elif command -v pkg >/dev/null; then
    PACKAGE_MANAGER="pkg"  # Termux
fi
ARCH=$(uname -m)
echo "Architecture: $ARCH"
# armv7, aarch64, x86_64
case "$ENVIRONMENT" in
    termux)
        echo "Running on Termux"

        # Ensure Python and zeroconf are installed
        if ! command -v python3 >/dev/null; then
            pkg install -y python
        fi
        pip3 install --user zeroconf

        echo "Starting python helper..."
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PYTHON_SCRIPT="$SCRIPT_DIR/discover_vla_star.py"
        # Loop until Python script finds a service
        while true; do
            FOUND=$(python3 $PYTHON_SCRIPT 2>/dev/null)
            if [ -n "$FOUND" ]; then
                NAME=$(echo "$FOUND" | awk '{print $1}')
                EMBODIED_VLA_STAR=$(echo "$FOUND" | awk '{print $2}')
                echo "Found embodied VLA* at $NAME@$EMBODIED_VLA_STAR"
                break
            fi
            sleep 1
        done
        ;;
    linux)
        echo "Running on Ubuntu/Debian"
        echo "Installing apt packages"
        apt install avahi-utils

        SERVICE="_bed._tcp"

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
        ;;
    *)
        echo "Unknown OS"
        ;;
esac





echo "======================================"
echo "Awakening..."
echo "======================================"
echo ""


#ssh "$NAME@$EMBODIED_VLA_STAR" 'bash -l -c "echo $OPENAI_API_KEY"; ./VLA_Star/experiments/run_embodied.sh;'
ssh -t "$NAME@$EMBODIED_VLA_STAR" \
"export OPENAI_API_KEY=$OPENAI_API_KEY; \
STAR=\$(./VLA_Star/experiments/script_that_outputs_name.sh); \
./VLA_Star/experiments/run_embodied.sh \$STAR"